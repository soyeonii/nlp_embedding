from MeCab_tokenizer import MeCab_tokenizer
from Sentencepiece_tokenizer import Sentencepiece_tokenizer
from Word2Vec_vectorizer import Word2Vec_vectorizer
from DB_connect import DB_connect
from File_processing import File_processing
from kss import split_sentences
import base64
import numpy as np

SELECT_SQL = "SELECT movie_id, plot FROM movie_plots"
INSERT_SQL = (
    "INSERT INTO movie_plot_embedding (movie_id, plot_embedding) VALUES (%s, %s)"
)
PRE_PATH = "data/"
MECAB_FILE = "mecab.txt"
MODEL_PREFIX = "setencepiece"
VOCAB_SIZE = "8000"
WORD2VEC_MODEL = "word2vec.model"


mecab = MeCab_tokenizer()
sentencepiece = Sentencepiece_tokenizer()
word2vec = Word2Vec_vectorizer(PRE_PATH + WORD2VEC_MODEL, 20)
db = DB_connect()
file = File_processing(PRE_PATH + MECAB_FILE)

# Mecab
data = db.select(SELECT_SQL)
plots = [plot for _, plot in data]
for plot in plots:
    sentences = split_sentences(plot)
    for sentence in sentences:
        mecab_tokens = mecab.tokenize(sentence)
        for token in mecab_tokens:
            file.write(token)

# Sentencepiece
plots_token = []
sentencepiece.model_train(PRE_PATH + MECAB_FILE, PRE_PATH + MODEL_PREFIX, VOCAB_SIZE)
sentencepiece_model = sentencepiece.model_load(PRE_PATH + MODEL_PREFIX + ".model")
for movie_id, plot in data:
    plot_token = []
    sentences = split_sentences(plot)
    for sentence in sentences:
        sentencepiece_tokens = sentencepiece.tokenize(sentencepiece_model, sentence)
        plot_token.append(sentencepiece_tokens)
    plots_token.append((movie_id, plot_token))

# Word2Vec
word2vec.model_train_save([plot_token for _, plot_token in plots_token])
word2vec_model = word2vec.model_load()
for movie_id, plot_token in plots_token:
    vector_list = np.float32(word2vec.vectorize(word2vec_model, plot_token)).tobytes()
    vector_tostring = base64.b85encode(vector_list).decode()
    db.insert(INSERT_SQL, (movie_id, vector_tostring))

db.close()
