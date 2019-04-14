#!/usr/bin/env python

# CPU frequency info.
file = open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq','r')
tmp = file.readline()
minfreq = int(tmp) / 1000
file.close()

file = open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq','r')
tmp = file.readline()
maxfreq = int(tmp) / 1000
file.close()

file = open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq','r')
tmp = file.readline()
curfreq = int(tmp) / 1000
file.close()


# Temperatures
file = open('/sys/bus/i2c/devices/1-0290/temp2_input','r')
tmp = file.readline()
cputemp = int(tmp) / 1000
file.close()

file = open('/sys/bus/i2c/devices/1-0290/temp1_input','r')
tmp = file.readline()
mbtemp = int(tmp) / 1000
file.close()

# Pipe menu
print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
print "<openbox_pipe_menu>"
print "  <item label=\"Minimum frequency: %dMHz\"/>" % minfreq
print "  <item label=\"Maximum frequency: %dMHz\"/>" % maxfreq
print "  <item label=\"Current frequency: %dMHz\"/>" % curfreq
print "  <separator />"
print "  <item label=\"CPU temp.: %dc\"/>" % cputemp
print "  <item label=\"M\B temp.: %dc\"/>" % mbtemp
print "</openbox_pipe_menu>"