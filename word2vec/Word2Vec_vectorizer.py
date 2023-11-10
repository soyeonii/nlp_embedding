from gensim.models import Word2Vec
import numpy as np


class Word2Vec_vectorizer:
    def __init__(self, model_path, vector_size):
        self.model_path = model_path
        self.vector_size = vector_size

    def model_train_save(self, text):
        model = Word2Vec(text, vector_size=100, window=5, min_count=5, workers=4, sg=0)
        model.save(self.model_path)

    def model_load(self):
        return Word2Vec.load(self.model_path)

    def vectorize(self, model, text):
        text_vector_list = []
        for line in text:
            line_vector_list = []
            for word in line:
                if word in model.wv.index_to_key:
                    line_vector_list.append(model.wv[word])
            text_vector_list.append(np.mean(line_vector_list, axis=0).tolist())
        return np.mean(text_vector_list, axis=0).tolist()
