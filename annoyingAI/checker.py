import os
import json
import falcon
import sys
import urllib.request
import urllib.error
import nltk
from collections import Counter
from sklearn.externals import joblib
from bs4 import BeautifulSoup

MODELS_DIR = 'models'
SERIALIZED_DIR = 'serialisations'
TEST_DIR = 'tests'
BASELINE = os.path.join(SERIALIZED_DIR, 'baselinev2.pkl')
VECTORIZER = os.path.join(SERIALIZED_DIR, 'vectorizer.pkl')
DUMMY_TRUTH = 'article2.txt'

from .baseline_model import Baseline as FactChecker
from .reuters_datasource import ReutersDatasource
from .srf_datasource import SRFDatasource
from .search_stance import (get_named_entities, filter_results,
    compute_topic_tfidf_relevance, compute_tfidf_relevance)
from .permid import PermidSender, token


def tfidf_filter(vectorizer, sent, texts, keep_maximum):
    filter_function = lambda s, t: compute_tfidf_relevance(vectorizer, s, t)
    return filter_results(sent, texts, filter_function, keep_maximum=keep_maximum)

def topic_tfidf_filter(sender, vectorizer, sent, texts, keep_maximum):
    filter_function = lambda s, t: compute_topic_tfidf_relevance(sender, vectorizer, s, t)
    return filter_results(sent, texts, filter_function, keep_maximum=keep_maximum)

def simple_keyword_extractor(sent):
    return [w for w in nltk.word_tokenize(sent) if w.isupper()]

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
        {'doc_id': doc['doc_id'], 'label': label, 'doc_text': doc['text']}
        for (label, _), doc in zip(labels_scores, related_docs)
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
    def __init__(self, path2model=BASELINE, path2vectorizer=VECTORIZER):
        self.fact_checker = FactChecker(path2model)
        print('Current dir: %s' % os.getcwd())
        self.rd = ReutersDatasource()
        self.srf = SRFDatasource()
        self.pm = PermidSender(token)
        self.vect = joblib.load(VECTORIZER)
        
    def clean_text(self, url):
        return simple_html_strip(url)
        
    def ssplit_text(self, text):
        return dummy_ssplit(text)
    
    def label_retrieved(self, sent, related_docs):
        # predict labels and probability scores for pairs of (sent, related_doc)
        return [self.fact_checker.give_label(sent, doc['text']) for doc in related_docs]
    
    def retrieve_related(self, sent, n=100,
                         keyword_extractor=simple_keyword_extractor,
                         # keyword_extractor=get_named_entities  #with billing enabled and a credit card
                         relevance_filter=tfidf_filter,
                         keep_maximum=6):
        
        # + extact keywords from input sentence `sent`
        # + using Reuters API, retrieve `n` relevant documents / videos
        # + filter them based on our own `relevance_filter`
        # + `keep_maximum` number of them for labeling
        # + handle videos?
        try:
            keywords = keyword_extractor(sent)
            if not keywords and keyword_extractor == simple_keyword_extractor:
                # try to back-off to something stupid
                keywords = simple_keyword_extractor(sent)
            if keywords:
                ids_headlines = self.rd.search_by_keyword(keywords,
                                                          limit=20,
                                                          label='Politics',
                                                          mediaType='V', # video
                                                          verbose=True)
            else:
                ids_headlines = []
        except urllib.error.HTTPError as e:
            print("Gracefully pretending it's not happening...")
            print('Keywords: ', keywords)
        #related = dummy_retrieve(sent)
        related = []
        for i, h in ids_headlines:
            if (i or i is not None):
                related.append({'doc_id':i, 'text':h})
                print('Related text: ', h)
            else: print('Seems nothing returned.')
                
        # use filter before labeling:
        filtered = []
        print('Rel: ', (lambda v, s, t, m: (None, t))(self.vect, sent, related, keep_maximum))
        for rel, doc in relevance_filter(self.vect, sent, related, keep_maximum):
            doc['rel_score'] = rel
            filtered.append(doc)
        return related
    
    def pick_best(self, sent_dict, labels_scores, related_docs):
        # rank retrieved docs for output
        # + simplest: B label and then by score
        # dummy_pick(sent_dict, labels_scores, related_docs)
        print('docs: ', related_docs)
        print('Counter: ', Counter([l for l, _ in labels_scores]))
        #sent_dict['results'], sent_dict['label'] = [], None
        if related_docs:
            majority_vote = Counter([l for l, _ in labels_scores]).most_common(1)[0][0]
            if majority_vote in ['agree', 'disagree', 'discuss']:
                sent_dict['label'] = majority_vote
                sent_dict['results'] = [{'doc_id': doc['doc_id'], 'doc_text': doc['text']}
                    for (l, _), doc in zip(labels_scores, related_docs) if l == majority_vote]
        print('sent_dict: ', sent_dict)
        return sent_dict    

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
            if ('results' not in sent_dict or
                not sent_dict['results']): continue  # Why is this not filtered??
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