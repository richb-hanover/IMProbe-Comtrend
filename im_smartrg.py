#!/usr/local/imdc/core/python/bin/imdc -OO
# The line above is required to run as an IMDC plugin

# im_smartrg.py - Intermapper probe for SmartRG 555 DSL modems
#
# Scrape web interface of a SmartRG 555 DSL modem to return its SNR values,
# and other important operational characteristics.
# Tested with SmartRG 555
#
# See the full documentation at: https://github.com/richb-hanover/IMProbe-Comtrend
#
# Demonstrates a detailed Command-line probe, using the IMDC Python interpreter,
# as well as the formatting available for a Status Window.
#
# ---------------------------------------------
# Copyright (c) 2017-2018 - Rich Brown, Blueberry Hill Software, http://blueberryhillsoftware.com
# MIT License - See LICENSE file for the full statement

# import os
import sys
import getopt
import urllib2
import base64
import re
# import socket
# import time
from datetime import datetime, timedelta

'''
pluginExit - return indicated response from the IMDC plugin
'''


def pluginExit(values, errMsg, exitCode):
    print "\{ %s }%s" % (values, errMsg)  # don't return anything except the errMsg as the probe's response
    sys.exit(exitCode)  # return "Down" exit status

'''
retrievePage() - get page from modem, handle errors
'''


def retrievePage(adrs, page, user, password):

    # Return test data during development
    # return open('/Users/richb/github/scrapecomtrend/RawData/statsadsl-smartRG.html', 'r').read()
    request = urllib2.Request('http://%s/%s' % (adrs, page))
    base64string = base64.b64encode('%s:%s' % (user, password))
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        result = urllib2.urlopen(request, timeout=3)
        return result.read()

    except urllib2.HTTPError, e:
        pluginExit("", "HTTP Error: %d %s" % (e.code, e.reason), 4)
    except urllib2.URLError, e:
        pluginExit("", "URL Error: %s"  % (e.reason), 4) # No values, Reason of "No response", exit code of 4 (down)

'''
index_containing_substring - scan the list for the first element that contains the substring
   https://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string
'''


def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

'''
scanForValues - scan the lines and return down and upstream values from the named line
'''


def scanForValues(name, lines):
    # data = [elem for elem in lines if name in elem ]
    # line = data[0]                     # get the first line with "name"
    ix = index_containing_substring(lines, name)
    line = lines[ix]
#    print "Line: %s" % (line)
    regex = re.compile(r'\d+')
    p = regex.findall(line)             # isolate numbers ("0.1 dB 119 156" => ['0', '1', '119', '156'])
    # print "Name: %s is %s" % (name, p[-2])
    vals = ["0", "0", "0", "0"]
    vals.extend(p)
    return vals[-4:]

'''
computeUpTime - given a number of seconds before now, determine when that interval began
'''


def computeUpTime(secs):
    outage = datetime.now() - timedelta(**{'seconds': secs})
    since = "%s" % outage.strftime("%d %b %H:%M:%S")
    return since


'''
scanForUpTime - scan for "Synchronized time and return time value
'''


def scanForUpTime(name, lines):
    ix = index_containing_substring(lines, name)
    line = lines[ix]
    regex = re.compile(r'\d+')
    p = regex.findall(line)
    time = ":".join(p[-4:])
    secs = computeSeconds(time)
    since = computeUpTime(secs)
    return [ time, secs, since ]

'''
computeSeconds - given string in form of \d+ sep \d+ sep \d+ sep \d+ that represents d, h, m, s,
    return number of seconds
'''


def computeSeconds(s):
    regex = re.compile(r'\d+')
    p = regex.findall(s)  # isolate numbers ("1d, 2h, 3m, 4s" => ['1', '2', '3', '4'])
    timeVals = ["0", "0", "0", "0"]
    timeVals.extend(p)  # Prepend four zero values in case nothing's there
    hrs = int(timeVals[-4]) * 24 + int(timeVals[-3])  # Days (4th from last) + Hours (third from last)
    mins = (hrs * 60) + int(timeVals[-2])  # Add minutes (second from last)
    secs = (mins * 60) + int(timeVals[-1])  # and seconds (last)
    return secs

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
        secs = computeSeconds(s)

        outage = datetime.now() - timedelta(**{'seconds': secs})
        since = "(Since %s)" % outage.strftime("%d %b %H:%M:%S")
        result.append(since)
    return result[0:6]                                          # return times & "since" values

'''
parseStats - parse the stats from the page at address/path
    Returns list of up/down SNR, Attenuation, and Power
'''


def parseStats(address, path, user, password):
    page = retrievePage(address, path, user, password)
    lines = page.split('<tr>')  # split on new <tr> elements
    try:
        # lines = list(filter(lambda x: '<tr>' in x, lines))
        x, y, dSNR, uSNR = scanForValues(">SNR Margin", lines)
        x, y, dAtten, uAtten = scanForValues(">Attenuation", lines)
        x, y, dPower, uPower = scanForValues(">Output Power", lines)
        x, y, dAttRate, uAttRate = scanForValues("Attainable Rate", lines)
        dActRate, uActRate, x, y = scanForValues(">Rate (", lines)
        upTime, upSecs, upSince = scanForUpTime(">Synchronized Time:", lines)
        return [ dSNR, uSNR, dAtten, uAtten, dPower, uPower, dAttRate, uAttRate, dActRate, uActRate, upTime, upSecs, upSince ]
    except ValueError, e:
        pluginExit("", "ValueError: %s" % (e.message), 4)
    except NameError, e:
        pluginExit("", "NameError: %s" % (e.message), 4)


'''
Main Routine - parse arguments, get data from modem, format the results
'''


try:
    searchString = ""
    opts, args = getopt.getopt(sys.argv[1:], "")
except getopt.GetoptError, err:
    searchString = "getopt error %d" % (err)
    args = []

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
dSNR0, uSNR0, dAtten0, uAtten0, dPower0, uPower0, dAttRate0, uAttRate0, dActRate0, uActRate0, upTime0, upSecs0, upSince0 = parseStats(address, "admin/statsadsl.cgi?bondingLineNum=0", user, password)
dSNR1, uSNR1, dAtten1, uAtten1, dPower1, uPower1, dAttRate1, uAttRate1, dActRate1, uActRate1, upTime1, upSecs1, upSince1 = parseStats(address, "admin/statsadsl.cgi?bondingLineNum=1", user, password)

# Retrieve uptime values
# page = retrievePage(address, "showuptime.html", user, password)
# times = scanForTimes(page)                 # scan off the Uptime, DSL uptime, pppoe uptime

try:
    reason = ""
    retcode=0                               # probe (system) exit code

    # Format the response for display in the Status Window

    print "\{ $dSNR0 := %s, $uSNR0 := %s, $dAtten0 := %s, $uAtten0 := %s, $dPower0 := %s, $uPower0 := %s, " \
                " $dAttRate0 := %s, $dActRate0 := %s, $uAttRate0 := %s, $uActRate0 := %s, $upTime0 := '%s', $upSecs0 := %s, $upSince0 := '%s', "  \
                " $dSNR1 := %s, $uSNR1 := %s, $dAtten1 := %s, $uAtten1 := %s, $dPower1 := %s, $uPower1 := %s, " \
                " $dAttRate1 := %s, $dActRate1 := %s, $uAttRate1 := %s, $uActRate1 := %s, $upTime1 := '%s', $upSecs1 := %s, $upSince1 := '%s' }" \
              % (dSNR0, uSNR0, dAtten0, uAtten0, dPower0, uPower0, dAttRate0, dActRate0, uAttRate0, uActRate0, upTime0, upSecs0, upSince0,
                 dSNR1, uSNR1, dAtten1, uAtten1, dPower1, uPower1, dAttRate1, dActRate1, uAttRate1, uActRate1, upTime1, upSecs1, upSince1)

    sys.exit(0)
except NameError, e:
    pluginExit("", "Name Error: %s" % (e.reason), 4)
# pluginExit(retstring, reason, retcode)
