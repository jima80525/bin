#!/usr/bin/perl
use strict;

my $tmpfile = "./jimawashere.tmp";
system("find . -name *.tgz > $tmpfile");

open(FILES, $tmpfile) || die("Could not open file: $tmpfile!");
my @lines = <FILES>;
close(FILES);
unlink($tmpfile);
foreach my $logname (@lines) {
   chomp $logname;
   print("logname is $logname\n");
   #logname is ./172.16.5.40/bug.tgz
   #logname is ./172.16.5.214/bug.tgz
   $logname =~ /\.\/([^\/]*)\//;
   my $ip = $1;
   print "think ip is $ip\n";
   rename($logname, ".\/$ip.tgz");
   system("rm -rf $ip");
}
