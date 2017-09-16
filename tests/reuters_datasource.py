#!/usr/bin/env python

import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import time

from xml.etree.ElementTree import ElementTree, fromstring

USERNAME = "HackZurichAPI"
PASSWORD = "8XtQb447"
AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/xml/"


class ReutersDatasource:

    def __init__(self, username=USERNAME, password=PASSWORD):
        self.authToken = None
        # get a new auth token every time, expires after a week
        tree = self._call('login',{'username':username,'password':password},True)
        if tree.tag == 'authToken':
            self.authToken = tree.text
        else:
            raise Exception('unable to obtain authToken')

    def _call(self, method, args={}, auth=False):
        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL
            args['token'] = self.authToken
        url = root_url + method + '?' + urllib.parse.urlencode(args)
        resp = urllib.request.urlopen(url, timeout=10)
        rawd = resp.read()
        return fromstring(rawd)  # parse xml    

    def call(self, method, args={}):
        return self._call(method, args, False)
    

def demo():
    # fet a list of all available channels
    rd = ReutersDatasource()
    tree = rd.call('channels')
    channels = [ {'alias':c.findtext('alias'),
                  'description':c.findtext('description')}
                 for c in tree.findall('channelInformation') ]
    print("List of channels:\n\talias\tdescription")
    print("\n".join(["\t%(alias)s\t%(description)s"%x for x in channels]))
        
    # fetch id's and headlines for a channel
    rd = ReutersDatasource()
    tree = rd.call('items',
                   {'channel':'AdG977',
                    'channelCategory':'OLR',
                    'limit':'10'})
    items = [ {'id':c.findtext('id'),
               'headline':c.findtext('headline')}
              for c in tree.findall('result') ]
    print("\n\nList of items:\n\tid\theadline")
    print("\n".join(["\t%(id)s\t%(headline)s"%x for x in items]))

if __name__=='__main__':
    demo()
