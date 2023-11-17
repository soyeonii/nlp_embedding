from Sentencepiece_tokenizer import Sentencepiece_tokenizer
from Word2Vec_vectorizer import Word2Vec_vectorizer
from GPT_embedding import GPT_embedding
from Cosine_similarity import Cosine_similarity
from DB_connect import DB_connect
from Encode_Decode import Encode_Decode

EMBEDDING_SELECT_SQL = "SELECT movie_id, word2vec FROM sentence_embedding_vectors"
# EMBEDDING_SELECT_SQL = "SELECT movie_id, word2vec FROM embedding_vectors"
PRE_PATH = "data/"
MODEL_PREFIX = "setencepiece"
WORD2VEC_MODEL = "word2vec.model"


sentencepiece = Sentencepiece_tokenizer()
word2vec = Word2Vec_vectorizer(PRE_PATH + WORD2VEC_MODEL)
gpt = GPT_embedding(
    "OPENAI_API_KEY", "text-embedding-ada-002"
)
cosine = Cosine_similarity()
db = DB_connect()
ed = Encode_Decode()

sentencepiece_model = sentencepiece.model_load(PRE_PATH + MODEL_PREFIX + ".model")
word2vec_model = word2vec.model_load()

# Consine similarity
embedding_data = []
for movie_id, vector_string in db.select(EMBEDDING_SELECT_SQL):
    vector_list = ed.decode(vector_string)
    embedding_data.append((movie_id, vector_list))

user_input = "세상을 울린 목소리"
# user_vector_list = gpt.vectorize(user_input)
user_input = sentencepiece.tokenize(sentencepiece_model, user_input)
user_vector_list = word2vec.vectorize(word2vec_model, [user_input])[0]
print()
movie_list = cosine.find_most_similar_movies(user_vector_list, embedding_data, 10)
for i, (movie_id, similarity) in enumerate(movie_list):
    print(
        f"{i+1:>2}.",
        db.select(f"SELECT title FROM movies WHERE id=({movie_id})")[0][0],
        "-",
        similarity,
    )
