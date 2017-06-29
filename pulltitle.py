#!/usr/bin/env python
"""
pulltitle.py - jenni Title Module
Copyleft 2016, @sairukau
Licensed under GPL2.0

This module reports url titles take from the channel 
"""

import re, os
import urllib2
import time

from StringIO import StringIO
import gzip
import ConfigParser

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("Could not find BeautifulSoup library,"
                      "please install to use the pulltitle module")



debug = True
conf = os.path.join(os.path.expanduser('~/.jenni'),'pulltitle.conf')
urlpattern = '.*[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+'

def buildconfig():
    with open(conf,'w') as f:
        f.write('[options]\nuser_agent=\nchannels=[""]\nwhitelist=[""]\ndebug=False')

def outconsole(string):
    if debug:
        print string
    return


def pulltitle(jenni, input):

    # check config each time, saves reloading script
    if not os.path.exists(conf):
        buildconfig()
        jenni.say("Pulltitle config created, now edit it")
        return
    else:
        config = ConfigParser.RawConfigParser()
        config.read(conf)

    try:
        user_agent = config.get('options','user_agent')
        channels = config.get('options','channels')
        whitelist = config.get('options','whitelist')
    except:
        jenni.say("Check configuration file")
        return


    nickqueue = []

    if input.sender.lower() in channels:
        # split on space
        inputspl = input.split()
        if input.nick not in nickqueue:
            outconsole(input.nick)
            nickqueue.append(input.nick)
            # loop through input list
            for item in inputspl:
                outconsole(item)
                outconsole(os.path.splitext(item)[-1])
                if item:
                    url = item
                    urlstr = item.split(' ')
                    outconsole(urlstr)
                    outconsole(url)
                    # reformat url
                    pu = urllib2.urlparse.urlparse(url)
                    urlscheme = pu.scheme
                    urlhostname = pu.netloc
                    if pu.scheme == '':
                        urlscheme = 'https'
                    url =  "%s://%s%s" % (urlscheme, urlhostname, pu.path)
                    if pu.netloc == '':
                        urlhostname = pu.path.split('/')[0]
                    topurl = "%s://%s" % (urlscheme, urlhostname)
                    data = False
                    outconsole(topurl) 
                    try:
                        # req url
                        req = urllib2.Request(url, headers={'Accept':'*/*'})
                        req.add_header('User-Agent', user_agent)
                        req.add_header('Accept-encoding', 'gzip')
                    
                        data = urllib2.urlopen(req)
                        outconsole(data)
                    except urllib2.URLError as e:
                        #jenni.say("Nope, sorry ... I can't find a title for %s" % url)
                        pass
                    except:
                        #jenni.say("No")
                        pass
                        return

                    if not data:
                        print " No data returned"
                        return

                    ### gzup
                    if data.info().get('Content-Encoding') == 'gzip':
                        buf = StringIO( data.read())
                        f = gzip.GzipFile(fileobj=buf)
                        data = f.read()
                    else:
                        data = data.read()

                    # find title
                    bs = BeautifulSoup(data.decode('utf-8','ignore'), "lxml")
                    if len(bs):
                        title = bs.find('title')

                        if title:
                            title = title.getText().strip()
                        else:
                            title = "No <title> found"
                    else:
                        title = "No data returned"

                    # output to channel 
                    jenni.say("[ %s ] - %s" % (title, topurl))

                    # floop prevention
                    time.sleep(0.8)
            
            nickqueue.remove(input.nick)
        else:
            jenni.say("%s: still processing your crap, wait until we are done" % input.nick)


pulltitle.rule = urlpattern
pulltitle.priority = 'high'
pulltitle.thread = False
    
if __name__ == "__main__":
    print __doc__.strip()
