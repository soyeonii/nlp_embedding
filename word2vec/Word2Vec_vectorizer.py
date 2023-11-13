from gensim.models import Word2Vec
import numpy as np
import multiprocessing


class Word2Vec_vectorizer:
    def __init__(self, model_path, vector_size):
        self.model_path = model_path
        self.vector_size = vector_size

    def model_train_save(self, text):
        model = Word2Vec(
            text,
            sg=1,
            vector_size=300,
            window=5,
            min_count=1,
            workers=multiprocessing.cpu_count(),
        )
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
        max_length = max(len(vec) for vec in text_vector_list if isinstance(vec, list))
        text_vector_list_padded = [
            vec + [0] * (max_length - len(vec))
            if isinstance(vec, list)
            else [0] * max_length
            for vec in text_vector_list
        ]
        result = np.mean(text_vector_list_padded, axis=0).tolist()
        # print("Word2Vec :", result)
        return result
