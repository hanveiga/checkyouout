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

import models.athene_system.fnc.refs.feature_engineering as fe
import models.athene_system.fnc.pipeline as pipe
from models.athene_system.fnc.refs.feature_engineering_challenge import *
from models.athene_system.fnc.refs.feature_eng import *

model_path = 'models/athene_system/data/fnc-1/mlp_models/voting_mlps_small_3_final_new_0/voting_mlps_small_3_final.sav'

class NeuralModel(object):
    def __init__(self, path):
        self._clf = self.load_model(path)
        self._labels = ['agree','disagree','discuss','unrelated']
        self.word_emb = WordEmbFeatures()

    def load_model(self,path):
        import pickle
        with open(path, 'rb') as handle:
            return pickle.load(handle)

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
        print('generate feature')
        X = self.generate_features_test(h, b)
        print('end generate feature')
        predicted = self._labels[int(self._clf.predict(X))]
        print(predicted)
        return predicted, self._clf.predict_proba(X)


    def generate_features_test(self, stances, dataset):
        """
        Equal to generate_features(), but creates features for the unlabeled test data
        """
        h, b, bodyId, headId = [], [], [], []

        feature_dict = {'overlap': fe.word_overlap_features,
                        'refuting': fe.refuting_features,
                        'polarity': fe.polarity_features,
                        'hand': fe.hand_features,
                        'latent_semantic_indexing_gensim_holdout_and_test': latent_semantic_indexing_gensim_holdout_and_test,
                        'NMF_fit_all_concat_300_and_test': self.word_emb.NMF_fit_all_concat_300_and_test_2,
                        'word_ngrams_concat_tf5000_l2_w_holdout_and_test':word_ngrams_concat_tf5000_l2_w_holdout_and_test,
                        'NMF_fit_all_incl_holdout_and_test': self.word_emb.NMF_fit_all_incl_holdout_and_test_2
                        }

        h = stances
        b = dataset
        feature_list = ['overlap', 'refuting', 'polarity', 'hand','NMF_fit_all_incl_holdout_and_test','NMF_fit_all_concat_300_and_test']

        X_feat = []
        for feature in feature_list:
            print("calculate feature: " + str(feature))
            feat = fe.gen_or_load_feats(feature_dict[feature], h, b)
            X_feat.append(feat)
        X = np.concatenate(X_feat, axis=1)
        return X


if __name__=='__main__':
    #model_path = os.path.join(SERIALIZED_DIR, sys.argv[1] + '.pkl')
    model_path = '../models/athene_system/data/fnc-1/mlp_models/voting_mlps_small_3_final_new_0/voting_mlps_small_3_final.sav'
    model = NeuralModel(path=model_path)
    stance = "Woman detained in Lebanon is not al-Baghdadi's wife, Iraq says"
    with open(os.path.join(TEST_DIR, 'article1.txt')) as f:
        text = f.read()
    a, b =model.give_label(stance, text)
    print(a)
