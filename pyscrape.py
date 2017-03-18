import urllib2
import base64

request = urllib2.Request('http://192.168.1.1/statsadsl.html')
base64string = base64.b64encode('%s:%s' % ('root', '12345'))
request.add_header("Authorization", "Basic %s" % base64string)
result = urllib2.urlopen(request)
# print result

content = result.read()
print content