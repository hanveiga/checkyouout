import os
import json
import falcon
import sys
import urllib.request
from bs4 import BeautifulSoup
#from reuters_datasource import ReutersDatasource

MODELS_DIR = 'models'
SERIALIZED_DIR = 'serialisations'
TEST_DIR = 'tests'
BASELINE = os.path.join(SERIALIZED_DIR, 'baselinev2.pkl')
DUMMY_TRUTH = 'article2.txt'

from .baseline_model import Baseline as FactChecker

def simple_html_strip(url, minimum_word_count=10,
                      ssplitter=lambda s: s.split(' ')):
    # returns a list of hopefully text
    with urllib.request.urlopen(url) as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    #article = soup.find('article')
    #if article: article = article.find_all('p')
    #else:
    article = soup.find_all('p')
    # sentence splitting might have to go in here...
    # indices for p tags or article.p tags
    text = []
    for i, s in enumerate(article):
        s = ''.join(list(s.stripped_strings))
        if len(ssplitter(s)) > minimum_word_count:
            out = {'p_id' : i, 'text' : s, 'results' : []}
            text.append(out)
    #print('Text out: ', text)
    return text

def dummy_retrieve(query, dummy_article=DUMMY_TRUTH):
    # ignores query
    with open(os.path.join(TEST_DIR, dummy_article)) as f:
        return [f.read()]    

def dummy_pick(sent_dict, labels_scores, related_docs):
    # ignores scores, adds some ids
    sent_dict['results'] = [
        {'doc_id': i, 'label': label, 'doc': doc}
        for i, ((label, _), doc) in enumerate(zip(labels_scores, related_docs))
        if label in ['agree', 'disagree', 'discuss']]  # , 'unrelated'
    return sent_dict  
    
def dummy_ssplit(text):
    return [{'id':0, 'text': text}]

def dummy_clean(url):
    return [url]
    
def msg(resp, body, code):
    resp.body = body
    print(body)
    resp.content_type = 'application/json'
    resp.status = code

def success_msg(resp, body, code=falcon.HTTP_200):
    msg(resp, body, code)
    
def error_msg(resp, body, code=falcon.HTTP_400):
    msg(resp, body, code)

class Resource:
    # * get input, act on text type and output clean sentence-split text
    #   + if url, get text, text process it??
    #   + video???
    #   + clean text
    # * for each sentence, search for related documents /  videos via Reuters API
    #   + clean the search docs
    #   + call model on them
    #   + produce labels
    # * pick subset of retrieved docs
    # * return urls, xmls for these docs / videos
    def __init__(self, path2model=BASELINE):
        self.fact_checker = FactChecker(path2model)
        print('Current dir: %s' % os.getcwd())
        #self.rd = ReutersDatasource()
        
    def clean_text(self, url):
        return simple_html_strip(url)
        
    def ssplit_text(self, text):
        return dummy_ssplit(text)
    
    def label_retrieved(self, sent, related_docs):
        # predict labels and probability scores for pairs of (sent, related_doc)
        return [self.fact_checker.give_label(sent, doc) for doc in related_docs]
    
    def retrieve_related(self, sent, n=100):
        # using Reuters API, retrieve `n` relevant documents / videos
        # and return as a list of ???
        # + handle videos?
        # + clean texts...
        #@TODO
        #self.rd.search_by_keyword(self, keyword,
        #                  limit=50,
        #                  label='Politics',
        #                  mediaType='V', # video
        #                  verbose=False)
        
        related = dummy_retrieve(sent)
        return related
    
    def pick_best(self, sent_dict, labels_scores, related_docs):
        # rank retrieved docs for output
        # + simplest: B label and then by score
        return dummy_pick(sent_dict, labels_scores, related_docs)

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf8'))
        print('Data: ', data)
        if 'url' in data:
            url = data['url']
            text = self.clean_text(url)
        else:
            assert 'text' in data
            text = data['text']
            #error_msg(resp, 'Unknown method.')
        print('Text: ', text)
        self.handle_text(resp, text)
        
    def handle_text(self, resp, ssplit_text):
        #print('Sentence-split Text: ', ssplit_text)
        print('Number of sentences: ', len(ssplit_text))
        outputs = []
        for sent_dict in ssplit_text:
            sent = sent_dict['text']
            related_docs = self.retrieve_related(sent)
            labels_scores = self.label_retrieved(sent, related_docs)
            output = self.pick_best(sent_dict, labels_scores, related_docs)
            if not sent_dict['results']: continue  # Why is this not filtered??
            outputs.append(output)
        print('Outputs: ', outputs)
        body = json.dumps(outputs, indent=True)
        print('Successfully fact-checked this: {}'.format(ssplit_text))
        success_msg(resp, body, code=falcon.HTTP_200)
        
class TextResource(Resource):    
    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf8'))
        ssplit_text = self.ssplit_text(data['text'])
        super().handle_text(resp, ssplit_text)

class UrlResource(Resource):
    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode('utf8'))
        text = super().clean_text(data['url'])
        # we need some sentence splitting here, too
        super().handle_text(resp, text)