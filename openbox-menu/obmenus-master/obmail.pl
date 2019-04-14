#!/usr/bin/perl

use strict;
use Mail::IMAPClient;
use IO::Socket::SSL;


print "<openbox_pipe_menu>\n<separator label=\"Gmail\" />\n";

my $username = '****';
my $password = '****';

my $socket;

unless ($socket = IO::Socket::SSL->new(
            PeerAddr => 'imap.gmail.com',
            PeerPort => 993)) {
    print "<item label=\"Cannot connect to internet.\" />\n";
    exit;
}

my $client;

unless ($client = Mail::IMAPClient->new(
            Socket   => $socket,
            User     => $username,
            Password => $password,
            Peek     => 1)) {
    print "<item label=\"Cannot open new client.\" />\n";
    exit;
}


if ($client->IsAuthenticated()) {
    my @unseen;

    $client->select("INBOX");
    @unseen = $client->unseen;

    if (@unseen) {
        foreach my $msg (@unseen) {
            my %mail;

            %mail = &getdata($msg);
            &printmenu(%mail);
        }
    } else {
        print "<item label=\"No new messages.\" />\n";
    }
} else {
    print "<item label=\"Authentication failure.\" />";
}

$client->logout();

print "<separator label=\"Email\" />\n";

my @newmail = `ls ~/mail/new`;

if (@newmail) {
    foreach (@newmail) {
        chomp;
        &readmail($_);
    }
} else {
    print "<item label=\"No new messages.\" />\n";
}

sub readmail {
    my ($filename) = @_;
    my %output;

    unless (open(EMAIL, $ENV{'HOME'}.'/mail/new/'.$filename)) {
        print "<item label=\"Cannot read message.\" />\n";
    } else {
        foreach my $line (<EMAIL>) {
            my @data;

            if ($line =~ /^Subject:\s/) {
                @data = split(' ', $line);
                shift(@data);
                $output{'Subject'} = join(' ', @data);
            } elsif ($line =~ /^From:\s/) {
                @data = split(' ', $line);
                shift(@data);
                $output{'From'} = join(' ', @data);
            }
        }
        &printmenu(%output);
    }
}

sub getdata {
    my ($uid) = @_;

    my %output = (
        From    => $client->get_header($uid, 'From'),
        Subject => $client->get_header($uid, 'Subject')
    ) or die "get_header(): $@";

    return %output;
}

sub printmenu {
    my (%msg) = @_;
    my $from = $msg{'From'} =~ s/\s*<.*>//r;
    my $subject = $msg{'Subject'};

    $from = &xmlclean($from);
    $subject = &xmlclean($subject);

    print "<item label=\"$from: $subject\" />\n";
}

sub xmlclean {
    my ($str) = @_;

    $str = $str =~ s/&/&amp;/gr;
    $str = $str =~ s/</&lt;/gr;
    $str = $str =~ s/>/&gt;/gr;
    $str = $str =~ s/'/&apos;/gr;
    $str = $str =~ s/"/&quot;/gr;
}

END {
    print "</openbox_pipe_menu>\n";
}
