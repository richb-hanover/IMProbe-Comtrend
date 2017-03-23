#!/usr/local/imdc/core/python/bin/imdc -OO
# The line above is required to run as an IMDC plugin

# Scrape the Comtrend modem to return its SNR values

import os
import sys
import getopt
import urllib2
import base64
import re
import socket

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
    line = data[0]                     # get the first line with "str"
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
    for str in data:                                              # only keep tail (with d:h:m:s values)
        s = str.replace(" days:", "d, ")
        s = s.replace(" hours:","h, ")
        s = s.replace(" mins:","m, ")
        s = s.replace(" secs","s")
        result.append(re.sub(r'.*<td>', '', s.replace('\n','')))
    return result[0:3]                                          # return first three entities

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

print "\{ $dSNR := %s, $uSNR := %s, $dAtten := %s, $uAtten := %s, $dPower := %s, $uPower := %s, $up := '%s', $dslUp := '%s', $pppUp := '%s' }" \
      % (dSNR, uSNR, dAtten, uAtten, dPower, uPower, times[0], times[1], times[2] )
sys.exit(retcode)

