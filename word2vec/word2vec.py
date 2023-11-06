from gensim.models import Word2Vec

model = Word2Vec.load('word2vec_model.model')

vector = model.wv['ìĬĪ']
print(vector)