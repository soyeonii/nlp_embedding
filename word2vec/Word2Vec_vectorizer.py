from gensim.models import Word2Vec


class Word2Vec_vectorizer:
    def __init__(self, model_path):
        self.model_path = model_path

    def model_train_save(self, text):
        model = Word2Vec(text, vector_size=100, window=5, min_count=5, workers=4, sg=0)
        model.save(self.model_path)

    def model_load(self):
        return Word2Vec.load(self.model_path)

    def vectorize(self, model, text):
        vector_list = []
        for line in text:
            for word in line:
                if word in model.wv.index_to_key:
                    vector_list.append(model.wv[word])
        return vector_list
