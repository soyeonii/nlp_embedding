from MeCab_tokenizer import MeCab_tokenizer
from Sentencepiece_tokenizer import Sentencepiece_tokenizer
from Word2Vec_vectorizer import Word2Vec_vectorizer
from GPT_embedding import GPT_embedding
from DB_connect import DB_connect
from File_processing import File_processing
from Encode_Decode import Encode_Decode
from kss import split_sentences

ORIGINAL_SELECT_SQL = "SELECT id, plot FROM movies"
# INSERT_SQL = "INSERT INTO embedding_vectors (movie_id, word2vec) VALUES (%s, %s)"
INSERT_SQL = (
    "INSERT INTO sentence_embedding_vectors (movie_id, word2vec) VALUES (%s, %s)"
)
PRE_PATH = "data/"
MECAB_FILE = "mecab.txt"
MODEL_PREFIX = "setencepiece"
VOCAB_SIZE = "16000"
WORD2VEC_MODEL = "word2vec.model"


mecab = MeCab_tokenizer()
sentencepiece = Sentencepiece_tokenizer()
word2vec = Word2Vec_vectorizer(PRE_PATH + WORD2VEC_MODEL)
# gpt = GPT_embedding(
#     "OPENAI_API_KEY", "text-embedding-ada-002"
# )
db = DB_connect()
file = File_processing(PRE_PATH + MECAB_FILE)
ed = Encode_Decode()

data = db.select(ORIGINAL_SELECT_SQL)
n = len(data)
# gpt_vector_list = []

# Mecab
plots = [plot for _, plot in data]
for plot in plots:
    sentences = split_sentences(plot)
    # gpt_vector_list.append(ed.encode(gpt.vectorize(sentences)))
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
word2vec.model_train_save(
    [token for _, plot_token in plots_token for token in plot_token]
)
word2vec_model = word2vec.model_load()
for i in range(n):
    movie_id, plot_token = plots_token[i]
    vector_list = word2vec.vectorize(word2vec_model, plot_token)
    ### sentence
    for vector in vector_list:
        vector_string = ed.encode(vector)
        db.insert(INSERT_SQL, (movie_id, vector_string))
    ### all
    # vector_string = ed.encode(vector_list)
    # db.insert(INSERT_SQL, (movie_id, vector_string))
