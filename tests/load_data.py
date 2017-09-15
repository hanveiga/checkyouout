from sklearn.externals import joblib
import sys

def load_classifier(path):
    clf = joblib.load(path)
    print(clf)

if __name__=='__main__':
    load_classifier(sys.argv[1])
