#!/usr/bin/perl

#use strict;
#use warnings;

my %CONFIG = (DF_COMMAND => 'df -Th');

sub get_partitions {

    my @partitions;
    open my $df_pipe, '-|', $CONFIG{DF_COMMAND};
    while (defined($df_pipe) and defined(my $line = <$df_pipe>)) {
        chomp($line);

        my ($fs, $type, $totalsize, $used, undef, $used_percent, $mountpoint) = split(' ', $line, 7);

        next if $type eq 'overlay';
        next if $mountpoint =~ m{^/(?>dev|sys|run|.*/\.cache)\b};

        $used_percent =~ s/^\d+\K%\z// or next;

        #my $name =
        #    $mountpoint eq '/' ? 'Root'
        #  : $mountpoint =~ m{^.*/}s ? ucfirst substr($mountpoint, $+[0])
        #  :                           ucfirst $mountpoint;

        push @partitions,
          scalar {
                  mountpoint   => $mountpoint,
                  used_percent => $used_percent,
                  total_size   => $totalsize,
                  used_size    => $used,
                 };
    }
    close $df_pipe;

    my %seen;
    return sort { length($a->{mountpoint}) <=> length($b->{mountpoint}) || $a->{mountpoint} cmp $b->{mountpoint} }
      grep { !$seen{join $;, %{$_}}++ } @partitions;
}

my @partitions = get_partitions();

print '${voffset -1}';

foreach my $i (0 .. $#partitions) {

    my $partition = $partitions[$i];
    print $i == 0 ? '${voffset 2}' : '${voffset -6}';

    my $icon = sprintf '%.0f', $partition->{used_percent} / 10;
    $icon = $icon > 9 ? 0 : $icon < 1 ? "A" : $icon;

    printf '${color0}${font Pie charts for maps:pixelsize=18}%s${font}${color}   '
      . '${voffset -5}%s ${font Termsyn:pixelsize=8}${alignr}${color1}%s / %4s${color}${font}${font}'
      . "\n\n", $icon, $partition->{mountpoint}, $partition->{used_size}, $partition->{total_size};
}
