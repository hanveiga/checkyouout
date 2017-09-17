import urllib.request, urllib.error, urllib.parse
import time
import json
import sys
#from lmxl import etree
from xml.etree.ElementTree import ElementTree, fromstring, tostring
from bs4 import BeautifulSoup

API_KEY = "AcUiqDvk0uG5FqjpjdUwFXbvbSJn9I1s"
SERVICE_URL = "http://srgssr-prod.apigee.net/integrationlayer/2.0/swi/"

class SRFDatasource:

    def __init__(self, api_key=API_KEY, service_url=SERVICE_URL):
        self.api_key = api_key
        self.service_url = service_url

    def call(self, method, args={}):
        args['apikey'] = self.api_key
        url = self.service_url + method + '?' + urllib.parse.urlencode(args)
        resp = urllib.request.urlopen(url, timeout=10)
        rawd = resp.read()
        #return fromstring(rawd)  # parse xml
        return json.loads(rawd.decode('utf8'))

    def search_by_keyword(self, keywords, pageSize=4, verbose=True):
        keywords = ' '.join(keywords)
        if verbose: print('Search query: ', keywords)
        id_results = []
        res = self.call('searchResultList/video',
            args={'q':keywords, 'pageSize':pageSize})
        print(res)
        try:
            if 'searchResultListMedia' in res:
                for r in res['searchResultListMedia']:
                    if verbose: print('Result: ', r)
                    urn = r.get('urn')
                    description = '. '.join([r.get('title', ''), r.get('description', '')])
                    id_results.append((urn, description))
        except Exception as e:
            raise e
        #if verbose: print('Search results: ', id_results)
        return id_results


if __name__=='__main__':
    # call me: python srf_datasource.py 'North Korea'
    id_result = []
    headline_result = []
    sd = SRFDatasource()
    id_result = sd.search_by_keyword([sys.argv[1]], verbose=True)
    #for retrieve_id, headline in id_result:
    #    if retrieve_id: rd.retrieve_item(retrieve_id, verbose=True)