from sklearn.externals import joblib
import numpy as np
import random
import os,sys,inspect
print(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = '..' #os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_DIR)
TEST_DIR = os.path.join(PROJECT_DIR, 'tests')
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
SERIALIZED_DIR = os.path.join(PROJECT_DIR, 'serialisations')


# Directory with models
#MODELS_DIR = os.path.dirname(__file__)
# Baseline model from http://www.fakenewschallenge.org/
#BASELINE_DIR = os.path.join(MODELS_DIR, 'baseline')
#sys.path.append(BASELINE_DIR)
# FakeNews challenge dataset & train/dev splits
#DATASET_DIR = os.path.join(BASELINE_DIR, 'fnc-1')
#BASE_DIR = os.path.join(BASELINE_DIR, 'splits')
# Serialzation directory

import models.baseline.feature_engineering as fe

class Baseline(object):
    def __init__(self, path):
        self._clf = self.load_model(path)
        self._labels = ['agree','disagree','discuss','unrelated']

    def load_model(self,path):
        clf = joblib.load(path)
        return clf

    def fit_features(self, h, b, name=0):
        name = str(name)
        #name = random.random()
        # check if there are features, add the rest
        X_overlap = fe.word_overlap_features(h, b)
        X_refuting = fe.refuting_features(h, b)
        X_polarity = fe.polarity_features(h, b)
        X_hand = fe.hand_features(h, b)

        X = np.c_[X_hand, X_polarity, X_refuting, X_overlap]
        return X

    def give_label(self, stance, body):

        """ stance - str 'headline'
            body - str 'article'
        """
        h = [stance]
        b = [body]
        X = self.fit_features(h, b)

        predicted = self._labels[int(self._clf.predict(X))]

        return predicted, self._clf.predict_proba(X)


if __name__=='__main__':
    model_path = os.path.join(SERIALIZED_DIR, sys.argv[1] + '.pkl')
    model = Baseline(path=model_path)
    stance = "Woman detained in Lebanon is not al-Baghdadi's wife, Iraq says"
    with open(os.path.join(TEST_DIR, 'article1.txt')) as f:
        text = f.read()
    a, b =model.give_label(stance, text)
    print(a)
