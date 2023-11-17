from gensim.models import Word2Vec
import numpy as np
import multiprocessing


class Word2Vec_vectorizer:
    def __init__(self, model_path):
        self.model_path = model_path

    def model_train_save(self, text):
        model = Word2Vec(
            text,
            sg=1,
            vector_size=300,
            window=5,
            min_count=2,
            workers=multiprocessing.cpu_count(),
            epochs=10,
        )
        model.save(self.model_path)

    def model_load(self):
        return Word2Vec.load(self.model_path)

    def vectorize(self, model, text):
        text_embedding_list = []
        for line in text:
            line_vector_list = []
            for word in line:
                if word in model.wv.index_to_key:
                    line_vector_list.append(model.wv[word])
            if line_vector_list:
                line_vector = np.mean(line_vector_list, axis=0)
                text_embedding_list.append(line_vector.tolist())
        return text_embedding_list

    # def vectorize(self, model, text):
    #     text_vector_list = []
    #     for line in text:
    #         line_vector_list = []
    #         for word in line:
    #             if word in model.wv.index_to_key:
    #                 line_vector_list.append(model.wv[word])
    #         text_vector_list.append(np.mean(line_vector_list, axis=0).tolist())
    #     max_length = max(len(vec) for vec in text_vector_list)
    #     text_vector_list_padded = [
    #         vec + [0] * (max_length - len(vec))
    #         for vec in text_vector_list
    #     ]
    #     result = np.mean(text_vector_list_padded, axis=0).tolist()
    #     return result
