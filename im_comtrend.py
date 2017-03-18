#!/usr/local/imdc/core/python/bin/imdc -OO
# The line above is required to run as an IMDC plugin

# Scrape the Comtrend modem to return its SNR values

import os
import sys
import getopt

try:
    searchString = ""
    opts, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError, err:
    searchString = "getopt error %d" % (err)
# if args[0] == "$numericParam":          # check to see if the argument is the name of the parameter
#     number = 0                          # if so, set it to a good initial value
# else:
#     number = int(args[0])               # otherwise, convert the string to an integer

# Read the stdin file which contains the search String
# f = sys.stdin # open stdin
# searchString = f.readline().strip()     # get the line & remove leading & trailing whitespace
# if (searchString == "$SearchString"):   # check to see if the value is the name of the parameter
#     searchString = ""                   # if so, set it to a good initial value

# Now to the work of the probe
# searchString += "a"                     # add another "a" to the end of the string
# number += 1                             # increment the number as well
# retstring = "Hunky Dory!"               # Return string

import urllib2
import base64
import re

request = urllib2.Request('http://192.168.1.1/statsadsl.html')
base64string = base64.b64encode('%s:%s' % ('root', '12345'))
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request)
ds = result
us = "not yet"

content = result.read()
lines = content.split('</tr>')

lines = [elem for elem in lines if 'SNR' in elem ]
print "Lines was: " + lines[0]

THIS NEXT LINE IS BROKEN
regex = r".*:([0-9]?)<.*([0-9]?)"
match = re.search(regex, lines[0])
print match
print match.group(1)

print "DS: %s, US: %s" % (match.group(1), match.group(2))

retstring = "" # "'*****'.join(lines)

retcode=0                               # probe (system) exit code

print "\{ $ds := '%s', $us := '%s' } %s" % (ds, us, retstring)
sys.exit(retcode)
