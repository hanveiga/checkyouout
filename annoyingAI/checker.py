import os
import json
import falcon
import sys

from xyz import FactChecker

# run as standalone script
#sys.path.append('..')

def msg(resp, body, code):
    resp.body = body
    print body
    resp.content_type = 'text'
    resp.status = code

def success_msg(resp, body, code=falcon.HTTP_200):
    msg(resp, body, code)
    
def error_msg(resp, body, code=falcon.HTTP_400):
    msg(resp, body, code)

class Resource(object):
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
    def __init__(self, path2model):
        self.fact_checker = FactChecker(path2model)
    
    def label_retrieved(self, sent, related_docs):
        # predict labels and probability scores for pairs of (sent, related_doc)
        return [fact_checker.predict(sent, doc) for doc in related_docs]
    
    def retrieve_related(self, sent, n=100):
        # using Reuters API, retrieve `n` relevant documents / videos
        # and return as a list of ???
        # + handle videos?
        # + clean texts...
        #@TODO
        related = [TEST_BODY]
        return related
    
    def pick_best(self, labels_scores):
        # rank retrieved docs for output
        # + simplest: B label and then by score
        return labels_scores[0][0]

    def on_get(self, req, resp):
        input_type = req.get_param('input_type')
        url = req.get_param('url', default=None)
        if input_type == 'url':
            clean_text = html2txt
        elif input_type == 'video':
            clean_text = video2txt
        elif input_type == 'clean':
            clean_text = lambda x: req.get_param('text')
        else:
            error_msg(resp, 'Unknown method.')
        text = clean_text(url)
        ssplit_text = ssplit_text(text)
        outputs = []
        for sent in ssplit_text:
            related_docs = self.retrieve_related(sent)
            labels_scores = self.label_retrieved(sent, related_docs)
            output = self.pick_best(labels_scores)
            outputs.append(output)
        resp.body = json.dumps(outputs)
        print('Successfully computed values for keys.')