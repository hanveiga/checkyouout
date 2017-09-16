from sklearn.externals import joblib
import numpy as np
import os,sys,inspect
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)
#sys.path.insert(0,parentdir)
import baseline as bs
import baseline.utils.score as sc
import baseline.feature_engineering as fe

PATH = 'features/'

class Baseline(object):
    def __init__(self, path):
        self._clf = self.load_model(path)
        self._labels = ['agree','disagree','discuss','unrelated']

    def load_model(self,path):
        clf = joblib.load(path)
        return clf

    def fit_features(self, h, b, name=0):
        # check if there are features, add the rest

        X_overlap = fe.gen_or_load_feats(fe.word_overlap_features, h, b, PATH + "overlap.{}.npy".format(name))
        X_refuting = fe.gen_or_load_feats(fe.refuting_features, h, b, PATH + "refuting.{}.npy".format(name))
        X_polarity = fe.gen_or_load_feats(fe.polarity_features, h, b, PATH + "polarity.{}.npy".format(name))
        X_hand = fe.gen_or_load_feats(fe.hand_features, h, b, PATH + "hand."+name+".npy")

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
