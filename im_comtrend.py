#!/usr/local/imdc/core/python/bin/imdc -OO
# The line above is required to run as an IMDC plugin

# im_comtrend.py - Intermapper probe for Comtrend DSL modems
# 
# Scrape web interface of a Comtrend DSL modem to return its SNR values, 
# and other important operational characteristics.
# Tested with Comtrend AR-5381U
#
# See the full documentation at: github
#
# Demonstrates a detailed Command-line probe, using the IMDC Python interpreter,
# as well as the formatting available for a Status Window.
#
# ---------------------------------------------
# Copyright (c) 2017 - Rich Brown, Blueberry Hill Software, http://blueberryhillsoftware.com
# MIT License - See the footer of the file for the full statement

import os
import sys
import getopt
import urllib2
import base64
import re
import socket
import time
from datetime import datetime, timedelta, date

'''
retrievePage() - get page from modem, handle errors
'''
def retrievePage(adrs, page, user, password):
    request = urllib2.Request('http://%s/%s' % (adrs,page))
    base64string = base64.b64encode('%s:%s' % (user, password))
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        result = urllib2.urlopen(request, timeout=3)
    except urllib2.URLError, e:
        # For Python 2.7
        # raise MyException("There was an error: %r" % e)
        print "\{ } No response"  # No response - timed out
        sys.exit(4)  # return "Down" exit status
    return result.read()

'''
scanForValues - scan the lines and return down and upstream values from the named line
'''
def scanForValues(name, lines):
    data = [elem for elem in lines if name in elem ]
    line = data[0]                     # get the first line with "name"
    regex = re.compile(r'\d+')
    p = regex.findall(line)             # isolate numbers ("0.1 dB 119 156" => ['0', '1', '119', '156'])
    return p[-2:]

'''
scanForTimes - scan the page and return the modem's uptime; the DSL uptime, and the pppoe uptime as strings
'''
def scanForTimes(page):
    lines = page.split('</td>')                                 # split on </td> elements
    data = [elem for elem in lines if '<td>' in elem]           # only keep lines with <td>
    result = []
    for str in data:
        # format the string to d, h, m, s
        s = str.replace('\n','')                                # trim off new lines
        s = re.sub(r'.*<td>', '', s)                            # trim off junk
        s = s.replace(" days:", "d, ")                          # format to d, h, m, s values
        s = s.replace(" hours:","h, ")
        s = s.replace(" mins:","m, ")
        s = s.replace(" secs","s")
        s = '%-19s' % s                                         # force into fixed width field
        result.append(s)

        # compute time of outage
        regex = re.compile(r'\d+')
        p = regex.findall(s)                            # isolate numbers ("1d, 2h, 3m, 4s" => ['1', '2', '3', '4'])
        timeVals = ["0","0","0","0"]
        timeVals.extend(p)                              # Prepend four zero values in case nothing's there
        hrs = int(timeVals[-4])*24+int(timeVals[-3])    # Days (4th from last) + Hours (third from last)
        mins = (hrs * 60) + int(timeVals[-2])           # Add minutes (second from last)
        secs = (mins * 60) + int(timeVals[-1])          # and seconds (last)
        # compute time of outage
        outage = datetime.now() - timedelta(**{'seconds': secs})
        since = "(Since %s)" % outage.strftime("%d %b %H:%M:%S")
        result.append(since)
    return result[0:6]                                          # return times & "since" values

'''
Main Routine - parse arguments, get data from modem, format the results
'''
try:
    searchString = ""
    opts, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError, err:
    searchString = "getopt error %d" % (err)

address = args[0]
# print "Address: %s" % (address)

if len(args) == 3:                          # if user & password args are on command line
    user = args[1]                          # (supplied when testing)
    password = args[2]
else:
    #                                       # Read the stdin file which contains the search String
    f = sys.stdin                           # open stdin
    credentials = f.readline().strip()      # get the line & remove leading & trailing whitespace
    # print "credentials: %s" % (credentials)
    #
    userpw = credentials.split(" ")
    user = userpw[0]
    password = userpw[1]

# Retrieve SNR, Power, Attenuation values
page = retrievePage(address, "statsadsl.html", user, password)
lines = page.split('</tr>')  # split on new <tr> elements
dSNR, uSNR = scanForValues("SNR", lines)
dAtten, uAtten = scanForValues("Attenuation", lines)
dPower, uPower = scanForValues("Output Power", lines)

# Retrieve uptime values
page = retrievePage(address, "showuptime.html", user, password)
times = scanForTimes(page)                 # scan off the Uptime, DSL uptime, pppoe uptime

retstring = ""
retcode=0                               # probe (system) exit code

# Format the response for display in the Status Window 
print "\{ $dSNR := %s, $uSNR := %s, $dAtten := %s, $uAtten := %s, $dPower := %s, $uPower := %s, $mdmUp := '%s', $mdmS := '%s', $dslUp := '%s', $dslS := '%s', $pppUp := '%s', $pppS := '%s' }" \
      % (dSNR, uSNR, dAtten, uAtten, dPower, uPower, times[0], times[1], times[2], times[3], times[4], times[5] )
sys.exit(retcode)

# ---------------------------
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
