from sklearn.externals import joblib
import sys
import numpy as np
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import models.baseline as bs
import models.baseline.utils.score as sc
import models.baseline.feature_engineering as fe


PATH = 'features/'
if not os.path.exists(PATH):
    os.makedirs(PATH)

def load_classifier(path):
    clf = joblib.load(path)
    return clf

def load_text(path):
    text = np.loadtxt(path)
    print(text)

def make_prediction(stance, body, clf):
    """ stance - str 'headline'
        body - str 'article'
    """
    h = [stance]
    b = [body]
    X = fit_features(h,b)

    print(clf.predict_proba(X))
    predicted = sc.LABELS[int(clf.predict(X))]

    print(predicted)

def fit_features(h, b, name='test'):

    X_overlap = fe.gen_or_load_feats(fe.word_overlap_features, h, b, PATH + "overlap."+name+".npy")
    X_refuting = fe.gen_or_load_feats(fe.refuting_features, h, b, PATH + "refuting."+name+".npy")
    X_polarity = fe.gen_or_load_feats(fe.polarity_features, h, b, PATH + "polarity."+name+".npy")
    X_hand = fe.gen_or_load_feats(fe.hand_features, h, b, PATH + "hand."+name+".npy")

    X = np.c_[X_hand, X_polarity, X_refuting, X_overlap]
    return X

if __name__=='__main__':
    clf = load_classifier(sys.argv[1])
    #load_text(sys.argv[1])

    with open('article1.txt') as f:
        text = f.read()
    stance = "Woman detained in Lebanon is not al-Baghdadi's wife, Iraq says"
    make_prediction(stance,text, clf)
