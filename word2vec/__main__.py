from MeCab_tokenizer import MeCab_tokenizer
from Sentencepiece_tokenizer import Sentencepiece_tokenizer
from Word2Vec_vectorizer import Word2Vec_vectorizer
from DB_connect import DB_connect
from File_processing import File_processing
from kss import split_sentences

SELECT_SQL = "SELECT plot FROM movie_plots"
PRE_PATH = "data/"
MECAB_FILE = "mecab.txt"
MODEL_PREFIX = "setencepiece"
VOCAB_SIZE = "10000"
WORD2VEC_MODEL = "word2vec.model"


mecab = MeCab_tokenizer()
sentencepiece = Sentencepiece_tokenizer()
word2vec = Word2Vec_vectorizer(PRE_PATH + WORD2VEC_MODEL)
db = DB_connect()
file = File_processing(PRE_PATH + MECAB_FILE)

# Mecab
data = db.select(SELECT_SQL)
plots = [plot[0] for plot in data]
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
for text in data:
    sentences = split_sentences(text[0])
    for sentence in sentences:
        sentencepiece_tokens = sentencepiece.tokenize(sentencepiece_model, sentence)
        plots_token.append(sentencepiece_tokens)

# Word2Vec
word2vec.model_train_save(plots_token)
word2vec_model = word2vec.model_load()
print(word2vec_model.wv.index_to_key)
for plot_token in plots_token:
    print(word2vec.vectorize(word2vec_model, plot_token))
