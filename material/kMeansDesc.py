from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

df = pd.read_excel('potext.xlsx')
descriptions = df['Purchase Order Text'].fillna('').tolist()

vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=1000)
X = vectorizer.fit_transform(descriptions)
kmeans = KMeans(n_clusters=10, random_state=42)
clusters = kmeans.fit_predict(X)
df['Cluster'] = clusters

df.to_csv('kMeansDescOutput.csv')