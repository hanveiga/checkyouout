#!/usr/bin/env python
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import time
import sys
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

rd = ReutersDatasource()

def search_by_keyword(keyword):
    keyword = '"'+keyword+'"'
    print(keyword)
    id_result = []
    res = rd.call('search',args={'q':'(main:'+keyword+')', 'language':'en'}) #||headline:USA OR Canada)||-headline:Bush'})
    for a in res:
        try:
            print (a.findall('id')[0].text)
            id_result.append(a.findall('id')[0].text)
            headline_result.append(a.findall('headline')[0].text)
            #print (a.findall('headline')[0].text)
            #print (a.findall('channel')[0].text)
        except:
            print('NA')
    return id_result


def retrieve_item(retrieve_id):
    rd = ReutersDatasource()
    tree = rd.call('item',args= {'id':retrieve_id,'entityMarkupField':'all','entityMarkup':'newsml'})
    for a in tree:
        print(a.tag,a.text)
        k = a.findall(a.tag)
        for b in k:
            print (b.tag)

    return tree

"""def demo():
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
"""

if __name__=='__main__':
    # call me: python reuters_datasource.py 'North Korea'
    id_result = []
    headline_result = []

    id_result = search_by_keyword(sys.argv[1])
    for  i in range(0,len(id_result)):
        print ("id: " + id_result[i], "channel: " + headline_result[i])
        retrieve_item(id_result[i])
