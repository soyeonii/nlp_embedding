from MeCab_tokenizer import MeCab_tokenizer
from Sentencepiece_tokenizer import Sentencepiece_tokenizer
from Word2Vec_vectorizer import Word2Vec_vectorizer
from GPT_embedding import GPT_embedding
from Cosine_similarity import Cosine_similarity
from DB_connect import DB_connect
from File_processing import File_processing
from Encode_Decode import Encode_Decode
from kss import split_sentences

ORIGINAL_SELECT_SQL = "SELECT movie_id, plot FROM movie_plots"
EMBEDDING_SELECT_SQL = "SELECT movie_id, plot_embedding FROM movie_plot_embedding"
INSERT_SQL = (
    "INSERT INTO movie_plot_embedding (movie_id, word2vec, gpt) VALUES (%s, %s, %s)"
)
PRE_PATH = "data/"
MECAB_FILE = "mecab.txt"
MODEL_PREFIX = "setencepiece"
VOCAB_SIZE = "16000"
WORD2VEC_MODEL = "word2vec.model"


mecab = MeCab_tokenizer()
sentencepiece = Sentencepiece_tokenizer()
word2vec = Word2Vec_vectorizer(PRE_PATH + WORD2VEC_MODEL, 20)
gpt = GPT_embedding(
    "OPENAI_API_KEY", "text-embedding-ada-002"
)
cosine = Cosine_similarity()
db = DB_connect()
file = File_processing(PRE_PATH + MECAB_FILE)
ed = Encode_Decode()

data = db.select(ORIGINAL_SELECT_SQL)
n = len(data)
gpt_vector_list = []

# Mecab
plots = [plot for _, plot in data]
for plot in plots:
    sentences = split_sentences(plot)
    gpt_vector_list.append(ed.encode(gpt.vectorize(sentences)))
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
    vector_string = ed.encode(vector_list)
    db.insert(INSERT_SQL, (movie_id, vector_string, gpt_vector_list[i]))

# Consine similarity
embedding_data = []
for movie_id, vector_string in db.select(EMBEDDING_SELECT_SQL):
    vector_list = ed.decode(vector_string)
    embedding_data.append((movie_id, vector_list))

user_input = "피자 가게에서 살아 움직이는 피자 가게 마스코트"
user_input = sentencepiece.tokenize(sentencepiece_model, user_input)
user_vector_list = word2vec.vectorize(word2vec_model, [user_input])
print("-- 가장 유사한 영화 목록 --")
movie_list = cosine.find_most_similar_movies(user_vector_list, embedding_data)
for i, (movie_id, similarity) in enumerate(movie_list):
    print(
        f"{i+1}.",
        db.select(f"SELECT title FROM movies WHERE id=({movie_id})")[0][0],
        "-",
        similarity,
    )

db.close()
