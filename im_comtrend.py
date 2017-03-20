#!/usr/local/imdc/core/python/bin/imdc -OO
# The line above is required to run as an IMDC plugin

# Scrape the Comtrend modem to return its SNR values

import os
import sys
import getopt
import urllib2
import base64
import re

try:
    searchString = ""
    opts, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError, err:
    searchString = "getopt error %d" % (err)

request = urllib2.Request('http://192.168.1.1/statsadsl.html')
base64string = base64.b64encode('%s:%s' % ('root', '12345'))
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request)

content = result.read()
lines = content.split('</tr>')      # split on new <tr> elements

lines = [elem for elem in lines if 'SNR' in elem ]
line = lines[0]                     # get the first line with "SNR"
regex = re.compile(r'\d+')
p = regex.findall(line)             # isolate numbers ("0.1 dB 119 156" => ['0', '1', '119', '156'])
# print "DS: %s, US: %s" % (p[2], p[3])

retstring = ""
retcode=0                               # probe (system) exit code

print "\{ $ds := '%s', $us := '%s' } %s" % (p[2], p[3], retstring)
sys.exit(retcode)
