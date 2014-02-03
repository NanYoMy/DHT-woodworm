#_*_ coding: utf-8 _*_
__author__="NanYoMy"

import urllib,urllib2,cookielib,re

def createCookieOpener():
    MTcookie = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
    opener = urllib2.build_opener(MTcookie)
    return opener

def getInfoByIp(ip):
    post_data={
    "ip":ip,
    "action":"2"
    }
    try:
        request=urllib2.Request("http://www.133ip.com/",urllib.urlencode(post_data))
        open=createCookieOpener()
        raw_html=open.open(request).read()
    except IOError,e:
        print e
        return
    
    token1=re.compile(r'(<font color=#0000FF>)(.+?)(</font>)',re.DOTALL)
    token2=re.compile(r'(<font color=#FF0000>)(.+?)(</font>)',re.DOTALL)
    token3=re.compile(r'(<font color=#FF00FF>)(.+?)(</font>)',re.DOTALL)

    for data1 in token1.findall(raw_html,re.MULTILINE):
        print data1[1]
        
                
    for data2 in token2.findall(raw_html,re.MULTILINE):
        print data2[1]
                
    for data3 in token3.findall(raw_html,re.MULTILINE):
        print data3[1]

    return ip+data3[1]+'\n'
    
with open('name.txt','w') as writer:           

    with open('ipAddress.txt','r') as file:
        while True:
            line =file.readline()
            if not line:
                break
            writer.write(getInfoByIp(line))
    
