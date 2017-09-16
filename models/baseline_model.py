from sklearn.externals import joblib
import numpy as np
import os,sys,inspect
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)
#sys.path.insert(0,parentdir)


# Directory with models
MODELS_DIR = os.path.dirname(__file__)
# Baseline model from http://www.fakenewschallenge.org/
BASELINE_DIR = os.path.join(MODELS_DIR, 'baseline')
sys.path.append(BASELINE_DIR)
# FakeNews challenge dataset & train/dev splits
#DATASET_DIR = os.path.join(BASELINE_DIR, 'fnc-1')
#BASE_DIR = os.path.join(BASELINE_DIR, 'splits')
# Serialzation directory
SERIALIZED_DIR = os.path.join(os.path.dirname(MODELS_DIR), 'serialisations')


import baseline as bs
import baseline.utils.score as sc
import baseline.feature_engineering as fe

# check if features folder exists in root/data/
os.path.append(__)
DATA_PATH = '../data/'
FEATURES_PATH = 'features/'
print(DATA_PATH+FEATURES_PATH)
if not os.path.exists(DATA_PATH+FEATURES_PATH):
    print('entered')
    os.mkdir(DATA_PATH+FEATURES_PATH)

FEATURES_PATH = DATA_PATH + FEATURES_PATH

class Baseline(object):
    def __init__(self, path):
        self._clf = self.load_model(path)
        self._labels = ['agree','disagree','discuss','unrelated']

    def load_model(self,path):
        clf = joblib.load(path)
        return clf

    def fit_features(self, h, b, name=0):
        # check if there are features, add the rest
        name = str(name)
        X_overlap = fe.gen_or_load_feats(fe.word_overlap_features, h, b, FEATURES_PATH + "overlap.{}.npy".format(name))
        X_refuting = fe.gen_or_load_feats(fe.refuting_features, h, b, FEATURES_PATH + "refuting.{}.npy".format(name))
        X_polarity = fe.gen_or_load_feats(fe.polarity_features, h, b, FEATURES_PATH + "polarity.{}.npy".format(name))
        X_hand = fe.gen_or_load_feats(fe.hand_features, h, b, FEATURES_PATH + "hand."+name+".npy")

        X = np.c_[X_hand, X_polarity, X_refuting, X_overlap]
        return X

    def give_label(self, stance, body):

        """ stance - str 'headline'
            body - str 'article'
        """
        h = [stance]
        b = [body]
        X = self.fit_features(h,b)

        predicted = self._labels[int(self._clf.predict(X))]

        return predicted, self._clf.predict_proba(X)


if __name__=='__main__':
    model = Baseline(sys.argv[1])
    stance = "Woman detained in Lebanon is not al-Baghdadi's wife, Iraq says"
    with open('../tests/article1.txt') as f:
        text = f.read()
    a, b =model.give_label(stance, text)
    print(a)
