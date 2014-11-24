#!/usr/bin/perl
use strict;
use File::Basename;


sub extractTars {
   my @list = ();
   while (my $filename = shift) {
      system("tar xf $filename");
      my $base = basename($filename,  ".tgz");
      rename("bugreport", $base);
      printf("created dir $base\n");
      push(@list, $base);
   }
   return @list;
}

sub createVersionFile {
   my $verfile = shift;
   printf("creating versions file $verfile\n");
   open(VFILE, ">$verfile") || die("Could not open file: $verfile!");
   my @list = sort @_;
   #while (my $dirname = shift) {
   foreach my $dirname (@list) {
      my $filename = $dirname . "/etc/version";
      open(VER, $filename) || die("Could not open file: $filename!");
      my $version=<VER>;
      close(VER);
      chomp($version);
      print VFILE "$dirname\t$version\n";
   }
   close(VFILE);
}

sub createChannelLogFile {
   while (my $dirname = shift) {
      my $logname = "$dirname.log";
      print "creating logfile $logname\n";
      # use bash to combine all the files and sort
      system("cat $dirname/var/log/* | sort > $logname");

      # now walk the file and substitute the channel name
      # normal line looks like
      # Mar 12 22:47:40 NET5404T-ABM0317 ProcMon: Process <deimos>, failed to ping me, attempting process restart
      # change to
      # Mar 12 22:47:40 $dirname ProcMon: Process <deimos>, failed to ping me, attempting process restart
      open(LOG, $logname) || die("Could not open file: $logname!");
      my @lines = <LOG>;
      close(LOG);
      my @newlines;
      foreach my $line (@lines) {
         $line =~ s/(^\w{3}?)\s{2}?/\1 0/;
         $line =~ s/(^\w{3}?\s+\d\d\s+\d\d:\d\d:\d\d )(\S*)(.*)/\1$dirname\3/;
         $line =~ s/^Jan/01Jan/;
         $line =~ s/^Feb/02Feb/;
         $line =~ s/^Mar/03Mar/;
         $line =~ s/^Apr/04Apr/;
         $line =~ s/^May/05May/;
         $line =~ s/^Jun/06Jun/;
         $line =~ s/^Jul/07Jul/;
         $line =~ s/^Aug/08Aug/;
         $line =~ s/^Sep/09Sep/;
         $line =~ s/^Oct/10Oct/;
         $line =~ s/^Nov/11Nov/;
         $line =~ s/^Dec/12Dec/;
         push(@newlines, $line);
      }
      open(LOG, ">$logname") || die("Could not open file: $logname!");
      foreach my $line (sort @newlines) {
         print LOG $line;
      }
      close(LOG);
   }
}

sub mergeLogs {
   my $logfile = shift;
   my $files = "";
   while (my $dirname = shift) {
      $files = $files . " $dirname.log";
   }


   #my $files = join ' ', @_;
   system("cat $files | sort > $logfile");
      open(LOG, $logfile) || die("Could not open file: $logfile!");
      my @lines = <LOG>;
      close(LOG);
      my @newlines;
      foreach my $line (@lines) {
         if ($line =~ /set to warn/) {
            $line =~ /(^\d\d\w{3}?\s+\d\d\s+\d\d:\d\d:\d\d )(\S*)(.*)/;
            push @newlines, "\nREBOOT $2\n";
         }
         push(@newlines, $line);
      }
      open(LOG, ">$logfile") || die("Could not open file: $logfile!");
      foreach my $line (@newlines) {
         print LOG $line;
      }
      close(LOG);
}

my @dirs = extractTars(@ARGV);
createVersionFile("versions.txt", @dirs);
createChannelLogFile(@dirs);
mergeLogs("alllogs.txt", @dirs);

