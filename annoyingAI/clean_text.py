import urllib.request
from bs4 import BeautifulSoup

def clean_text(url):
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f)
    return list(BeautifulSoup(f).find('article').stripped_strings)