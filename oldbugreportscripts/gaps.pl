#!/usr/bin/perl
use strict;
use DateTime;
use DateTimeX::Easy;

sub getTimeStruct {
   my $line = shift @_;
#   03Mar 27 10:16:57 Cam0803 syslog[1019]: ERROR    MCP - resetting video type to unknown due to too many polls at unknown
   $line =~ /^\d\d(\w\w\w\s\d\d\s\d\d:\d\d:\d\d)/;
   return DateTimeX::Easy->new($1);
   #return DateTimeX::Easy->new("Mar 27 10:16:57");
}

sub compareTimesAndReturnStringIfBig {
   my $oldTime = shift @_;
   my $newTime = shift @_;
   $oldTime || die "oldtime was null";
   $newTime || die "newtime was null";

   my $diff = $newTime->subtract_datetime($oldTime);

   my $hr  = DateTime::Duration->new(hours => 1);
   my $retStr = "";
   if ($diff->compare($diff, $hr, $oldTime) > 0) {
      $retStr = sprintf("\n[Gap of %d Months %d weeks %d days %d hours %d minutes %d seconds]\n\n",
         $diff->months,
         $diff->weeks,
         $diff->days,
         $diff->hours,
         $diff->minutes,
         $diff->seconds);
   }
   return $retStr;
}

while (my $logname = shift) {
#my $logname = shift;

   printf("opening $logname\n");
   open(LOG, $logname) || die("Could not open file: $logname!");
   my @lines = <LOG>;
   close(LOG);
   my $oldTime = getTimeStruct($lines[0]);
#die;

   my @newlines;
   my $num = 1;
   foreach my $line (@lines) {
      $num = $num + 1;
      my $newTime = getTimeStruct($line);
      my $gapString = compareTimesAndReturnStringIfBig($oldTime, $newTime);
      if ($gapString ne "") {
         push(@newlines, $gapString);
      }
      push(@newlines, $line);
      $oldTime = $newTime->clone();
   }
   open(LOG, ">$logname") || die("Could not open file: $logname!");
   foreach my $line (@newlines) {
      print LOG $line;
   }
   close(LOG);
}

if (0) {
my $ndt = DateTimeX::Easy->new("Mar 27 14:03:59");
my $dt = DateTimeX::Easy->new("Mar 27 19:02:59");

my $diff = $ndt->subtract_datetime($dt);

my $hr  = DateTime::Duration->new(hours => 1);
if ($diff->compare($diff, $hr, $dt) > 0) {
   print "more than 1 hour\n";
}


printf("[Gap of %d Months %d weeks %d days %d hours %d minutes %d seconds]\n",
  $diff->months,
  $diff->weeks,
  $diff->days,
  $diff->hours,
  $diff->minutes,
  $diff->seconds);

}
