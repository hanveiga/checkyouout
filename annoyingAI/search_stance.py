import os
import nltk
import json
from sklearn.metrics.pairwise import cosine_distances
from sklearn.externals import joblib

from .analyze import analyze_entities
from .permid import PermidSender, token

SERIALIZED_DIR = 'serialisations'
VECTORIZER = os.path.join(SERIALIZED_DIR, 'vectorizer.pkl')

GOOGLEAPIKEY = 'AIzaSyDjPD2VBeUpBtxm6rN-UM6BFvnHtSAHIJo'

def get_named_entities(sentence):
    response = analyze_entities(sentence)
    named_entities = []
    for entity in response['entities']:
        #print(entity['type'])
        if entity['type'] != 'COMMON':
            #print(entity['name'])
            named_entities.append(entity['name'])
        #named_entities.append(ent.text)

    return named_entities #named_entities


def pick_sentences(article):
    #receives article and picks sentences to be fact checked
    # returns list of sentences to be checked
    split_by_sentences = nltk.word_tokenize(article)
    filtered_sentences = []
    #for sentence in split_by_sentences:
    #    entities = get_named_entities(sentence)
    #    if entities > 2:
    #        filtered_sentences.append([sentence,entities])
    return split_by_sentences

def search_with_sentence(sentence):
    # generate keywords
    keywords = get_named_entities(sentence)
    #print(keywords)
    results = []
    # search keywords using rd
    for keyword in keywords:
        retrieved_results = search_by_keyword(keyword)
        results = results + retrieved_results
    # return list of results
    return results

def search_by_keyword(keyword):
    return []

def filter_results(sentence, list_of_results, compute_relevance, keep_maximum=5):
    relevances = []
    for result in list_of_results:
        # result is a dict with a "text" key
        relevances.append(compute_relevance(sentence, result['text']))
        # takes list of results from reuters and returns

    rels_candidates = []
    for i in range(keep_maximum):
        try:
            rels_candidates.append(sorted(zip(relevances, list_of_results),
                                     key = lambda x: x[0], reverse=True).pop())
        except:
            print('not enough candidates')

    return rels_candidates # are not dicts but tuples


def compute_tfidf_relevance(vectorizer, sentence, text):
    # vectorizer e.g. vectorizer = joblib.load('../serialisations/vectorizer.pkl')
    a = vectorizer.transform([sentence])
    b = vectorizer.transform([text])
    return cosine_distances(a, b)


def compute_topic_tfidf_relevance(sender, vectorizer, sentence, text, lamb=0.3):
    # sender is a PermID sender
    distance = compute_tfidf_relevance(vectorizer, sentence, text)
    topica = sender.get_topics(sentence)
    topicb = sender.get_topics(text)
    topics = (len(set(topica).intersection(topicb))+1)/float(len(topicb)+1.)
    value = (1-lamb)*distance + lamb*topics
    return value

def test_relevance_of_results(sentence, parent_article, item):
    # eats stance, parent_article (or other stuff and an reuters item
    # returns yes or no
    pass

if __name__=='__main__':
    #with open('../tests/article1.txt') as f:
    #    text = f.read()
    #sentences = pick_sentences(text)
    #print (sentences)

    sender = PermidSender(token)
    topics = sender.get_topics('Obama Care was repealled.')
    print(topics)
    val = compute_topic_tfidf_relevance(sender, joblib.load(VECTORIZER),
        'This is bullshit', 'There was a lot of bullshit happening in ZH that day.')
    print (val)
    #for sentence in sentences:
    #    search_with_sentence(sentence)
