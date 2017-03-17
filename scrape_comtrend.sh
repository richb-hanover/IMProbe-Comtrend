#! /bin/sh
# Scrape Comtrend SNR

curl -s -N http://root:12345@192.168.1.1/statsadsl.html | \
sed -E 's|</tr>|</tr>\
|g' | \
grep 'SNR Margin' | \
sed -E 's|.*:</td><td>([0-9]*)</td><td>([0-9]*)</td></tr>| SNR: \1  \2|g' | \
cat 

# Documentation:
#
# curl -N fix: - no buffering
#    http://stackoverflow.com/questions/16703647/why-curl-return-and-error-23-failed-writing-body
# curl -s - silent, no progress output