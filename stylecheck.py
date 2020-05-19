#!/usr/bin/env python3
import os
import re
import sys
from timeit import default_timer as timer

def remove_quotes(line):
    '''  this part is kind if a hack, but it makes life much easier...  convert
    all strings to a placeholder X, the idea being that X by itself will never
    violate a standard, but the string might '''
    # replace single-quoted characters (e.g. '=', '+', '"') with 'X'
    line = re.sub(r"'[^']*'", 'X', line)

    # first replace embedded \" sequences with X
    line = re.sub(r'\\"', 'X', line)

    # then replace the whole thing with "X"
    line = re.sub(r'"[^"]*"', 'X', line)
    return line

def strip_comments(line, inCommentBlock):
    if (inCommentBlock):
        # see if the comment block ends on this line
        if re.search('\*/', line):
            line = re.split('\*/', line, maxsplit=1)[1]
            inCommentBlock = False
        else:
            line = ''

    # check for comments in the current line
    # remove end of line // comments
    line = re.sub(r'\s*//.*$', '', line)

    # see if the line starts a new comment block
    # NOTE: There's a degenerate case of a block comment starting and ending
    # on the same line and then ANOTHER block starting that will cause this
    # to fail.
    if re.search(r'/\*', line):
        # if it also ends the block, it's easy
        if re.search('\*/', line):
            line = re.sub(r'/\*.*\*/', '', line)
        else:
            inCommentBlock = True
            line = re.split('/\*', line, maxsplit=1)[0]

    return line, inCommentBlock


def check_bad_chars(line, number, errors):
    # only allow valid whitespace
    if re.search(r'\t', line):
        errors.append((number, "Illegal tab character"))

    # indicates trailing whitespace at the end of a line
    if re.search(r' +$', line):
        errors.append((number, "Trailing whitespace not allowed"))


def check_header_line(line, number, errors):
    header = [
        "//============================================================================",
        "// Copyright \\(c\\) 20[\\d][\\d]([,-][\\d]+)* Pelco\\. All rights reserved\\.",
        "//",
        "// This file contains trade secrets of Pelco.  No part may be reproduced or",
        "// transmitted in any form by any means or for any purpose without the express",
        "// written permission of Pelco.",
        "//============================================================================",
    ]

    if number < len(header):
        if not re.match(header[number], line):
            errors.append((number, "Missing required header"))


def check_whitespace(line, number, errors):
    # no whitespace allowed before semi-colons at the end of a statement
    if re.search(r'\s;$', line):
        errors.append((number, "No whitespace before semicolons"))

    # check parenthesis for extra whitespace
    if re.search(r'\(\s+[^;]*\s+\)', line) or \
       re.search(r'\([^;]*\s+\)', line) or \
       re.search(r'\(\s+[^;]*\)', line):
        errors.append((number, "Extra whitespace at parenthesis"))

    # check pre-processor statments alignment
    if re.search(r'^\s+#', line):
        errors.append((number, "Pre-processor statements must be aligned far left"))


def check_control_blocks(line, number, errors):
    # check to make sure that control statements have whitespace
    match = re.search(r'\b((if)|(else)|(switch)|(for)|(do)|(while)|(return))\b\S+', line)
    if match:
        errors.append((number, "Missing whitespace '{0}'".format(match.group(1))))

    # check if-statement construction
    # catch "if (\n"
    if re.search(r'\bif\b\s+\($', line):
        errors.append((number, "Invalid if-statement construction"))

    # check for-loop construction
    # looking for spacing around ; and :
    if re.search(r'\bfor\b\s+\(', line) and \
       not re.search(r'\bfor\b\s+\(((.*\S)|( )); ((.*\S)|()); ((.*\S)|())\)', line) and \
       not re.search(r'\bfor\b\s+\(.*\s:\s.*\)', line):
        errors.append((number, "Invalid for-loop construction"))

    # check while-loop construction
    if re.search(r'^[^)]+\bwhile\b\s+\(', line) and \
       not re.search(r'\bwhile\b\s+\(.*\)', line):
        errors.append((number, "Invalid while-loop construction"))

    # check empty loop statements
    if re.search(r'\b((for)|((?<!} )while))\b\s+\(.*\)\s*;$', line):
        errors.append((number, "Invalid loop construction: use '{ }' for empty loops"))


def check_braces(line, number, errors):
    # braces must not be the first thing on a line
    if re.search(r'^\s*{', line):
        errors.append((number, "Invalid brace placement"))

    # braces should not be adjacent to anything but whitespace
    if re.search(r'(\S\{)|({\S)|(\S}(?![;,]))|(}(?![;,])\S)', line):
        errors.append((number, "Braces must have surrounding whitespace"))


def check_operators(line, number, errors):
    # this part gets a little nasty, so I broke it up into a few lines we
    # won't try to match every operator, since some things (like '-') shows
    # up as a math operator and a negative sign  --jah
    REGEX_LOGICAL_GROUP = "(&&)|(\|\|)"
    # '(?<!' is a 'zero-width negative look-behind assertion'  sheesh
    REGEX_LOGICAL_OPER  = "([!=]=)|((?<!<)<=)|((?<!>)>=)"
    REGEX_BITWISE_OPER  = "(<<=)|(>>=)|(\^=)"
    REGEX_ASSIGN_OPER   = "(?<![%!=+\-*/&\|<>\^])=(?!=)"
    REGEX_MATH_OPER     = "([*+-/%]=)"

    # match all possibilities for operators
    REGEX_OPERATORS = "(" \
                + REGEX_LOGICAL_OPER + "|" \
                + REGEX_LOGICAL_GROUP + "|" \
                + REGEX_BITWISE_OPER + "|" \
                + REGEX_ASSIGN_OPER + "|" \
                + REGEX_MATH_OPER \
                + ")"

    # perform the whitespace rules for operators in a single swoop
    match = re.search(r'\S{0}|{0}\S'.format(REGEX_OPERATORS), line)
    if match:
        # the positions numbers are empirically derrived
        oper = match.group(1)
        if not oper:
            oper = match.group(11)
        errors.append((number, "Missing whitespace around operator '{0}'".format(oper)))

    # perform the whitespace rules for logical groups
    if re.search(r'([^\s\)]\s+({0}))|(({0})\s+[^\s\(])'.format(REGEX_LOGICAL_GROUP), line):
        errors.append((number, "Logical groups must be enclosed in parenthesis"))

def read_and_test_lines(filename):
    inCommentBlock = False  # keeps track of whether we're inside a block comment or not
    errors = list()

    # slurp up the entire file contents
    with open(filename, 'r') as fp:
        lines = fp.readlines()

    # process the file contents
    for number, line in enumerate(lines):
        # check for bad characters before we modify the line
        check_bad_chars(line, number, errors)

        # check for properly formed header
        check_header_line(line, number, errors)

        # load any style check options on the line
        # load_opts($_)
        # JHA TODO

        line = remove_quotes(line)
        line, inCommentBlock = strip_comments(line, inCommentBlock)

        check_whitespace(line, number, errors)
        check_control_blocks(line, number, errors)
        check_braces(line, number, errors)
        check_operators(line, number, errors)

    if re.search(r'^\s*$', lines[-1]):
        errors.append((len(lines)-1, "Extra newline at end of file"))

    return errors, len(lines)


def display_errors(filename, errors):
    for number, error in errors:
        print("{0}:{1}: {2}".format(filename, int(number)+1, error))


def parse_file(filename):
    # reset for this file
    # currentOptions = dict()

    # load the file and parse
    errors, numberLines = read_and_test_lines(filename)

    display_errors(filename, errors)
    return len(errors), numberLines


def process_directory(rootDir):
    fileCount = 0
    errorCount = 0
    lineCount = 0
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if re.search(r'(\.cpp$)|(\.c$)|(\.hpp$)|(\.h$)', fname):
                fileCount += 1
                errors, lines = parse_file(os.path.join(dirName, fname))
                errorCount += errors
                lineCount += lines
    return fileCount, errorCount, lineCount

def main():
    total_files = 0
    total_errors = 0
    total_lines = 0
    if len(sys.argv) > 1:
        for file in sys.argv[1:]:
            if os.path.isfile(file):
                files = 1
                errors, lines = parse_file(file)
            elif os.path.isdir(file):
                files, errors, lines = process_directory(file)
            total_files += files
            total_errors += errors
            total_lines += lines
    else:
        total_files, total_errors, total_lines = process_directory(os.getcwd())

    return total_files, total_errors, total_lines

if __name__ == '__main__':
    start = timer()
    files, errors, lines = main()
    stop = timer()

    # print time statistics
    if files > 0:
        elapsed = (stop - start);
        print("Parsed {0} files: found {1} errors in {2} lines." \
              " ({3:f} secs, {4:f} ms/file)".format(files, errors, lines, elapsed,
                                                    elapsed * 1000 / files))
    else:
        print("No files scanned")
    sys.exit(errors)
