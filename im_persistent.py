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
if args[0] == "$numericParam":          # check to see if the argument is the name of the parameter
    number = 0                          # if so, set it to a good initial value
else:
    number = int(args[0])               # otherwise, convert the string to an integer

# Read the stdin file which contains the search String
f = sys.stdin # open stdin
searchString = f.readline().strip()     # get the line & remove leading & trailing whitespace
if (searchString == "$SearchString"):   # check to see if the value is the name of the parameter
    searchString = ""                   # if so, set it to a good initial value

# Now to the work of the probe
searchString += "a"                     # add another "a" to the end of the string
number += 1                             # increment the number as well
retstring = "Hunky Dory!"               # Return string
retcode=0                               # probe (system) exit code

print "\{ $SearchString := '%s', $numericParam := '%d' } %s" % (searchString, number, retstring)
sys.exit(retcode)
