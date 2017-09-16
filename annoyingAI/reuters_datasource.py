import urllib.request, urllib.error, urllib.parse
import time
import sys
#from lmxl import etree
from xml.etree.ElementTree import ElementTree, fromstring, tostring
from bs4 import BeautifulSoup

USERNAME = "chris.blatchfordAPI" #"HackZurichAPI"
PASSWORD = "Ce88t6cU" #"8XtQb447"
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

    def search_by_keyword(self, keywords,
                          limit=50,
                          label='Politics',
                          mediaType='V', # video
                          verbose=False):
        keywords = ['"{}"'.format(k) if ' ' in k else k for k in keywords]
        keyword = ' AND '.join(keywords)
        if verbose: print('Search query: ', keyword)
        id_results = []
        res = self.call('search',
                        args={'q':'(main:'+keyword+')',
                              'language':'en',
                              'sort':'score',
                              'label':label,
                              'mediaType':mediaType,
                              'limit':limit}) #||headline:USA OR Canada)||-headline:Bush'})
        for a in res:
            try:
                #print(tostring(a))
                item_id = a.findtext('id')
                item_headline = a.findtext('headline')
                id_results.append((item_id, item_headline))
                #print (a.findall('channel')[0].text)
            except Exception as e:
                raise e
                #print('NA')
        if verbose: print('Search results: ', id_results)
        return id_results


    def retrieve_item(self, retrieve_id, verbose=False):
        print('# Retrieving item with id: ', retrieve_id)
        res = self.call('item',
                        args={'id':retrieve_id,
                              #'entityMarkupField':'all',
                              #'entityMarkup':'newsml'
                             })
        for a in res:
            if verbose:
                sys.stdout.write(tostring(a).decode('utf8'))
                print
                print
        return res

if __name__=='__main__':
    # call me: python reuters_datasource.py 'North Korea'
    id_result = []
    headline_result = []
    rd = ReutersDatasource()
    id_result = rd.search_by_keyword([sys.argv[1]], limit=100, verbose=True)
    for retrieve_id, headline in id_result:
        if retrieve_id: rd.retrieve_item(retrieve_id, verbose=True)