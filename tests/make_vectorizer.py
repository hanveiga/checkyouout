from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
newsgroups_train = fetch_20newsgroups(subset='train')
vectorizer = TfidfVectorizer(stop_words='english')
vectors = vectorizer.fit_transform(newsgroups_train.data)
print(vectors.shape)
joblib.dump(vectorizer, 'vectorizer.pkl')
