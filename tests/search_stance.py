import nltk.data
import spacy
import analyze as an
import json
from sklearn.metrics.pairwise import cosine_distances
from sklearn.externals import joblib

vectorizer = joblib.load('../serialisations/vectorizer.pkl')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
GOOGLEAPIKEY = 'AIzaSyDjPD2VBeUpBtxm6rN-UM6BFvnHtSAHIJo'

def get_named_entities(sentence):
    response = an.analyze_entities(sentence)
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
    split_by_sentences = tokenizer.tokenize(article)
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

def filter_results(sentence, list_of_results):
    relevances = []
    for result in list_of_results:
        #text = exctract_text(result)
        relevances.append(compute_relevance(sentence, result))
        # takes list of results from reuters and returns

    candidates = []
    for i in range(3):
        try:
            candidates.append(sorted(zip(relevances, list_of_results), key = lambda x: x[0], reverse=True).pop())
        except:
            print('not enough candidates')

    return candidates

def compute_relevance(sentence, text):
    a = vectorizer.transform([sentence])
    b = vectorizer.transform([text])
    value = cosine_distances(a,b)
    print(value)

    return

def test_relevance_of_results(sentence, parent_article, item):
    # eats stance, parent_article (or other stuff and an reuters item
    # returns yes or no
    pass

if __name__=='__main__':
    #with open('../tests/article1.txt') as f:
    #    text = f.read()
    #sentences = pick_sentences(text)
    #print (sentences)
    compute_relevance('This is bullshit','There was a lot of bullshit happening in ZH that day.')
    #for sentence in sentences:
    #    search_with_sentence(sentence)
