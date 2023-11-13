from sklearn.metrics.pairwise import cosine_similarity


class Cosine_similarity:
    def calculate_cosine_similarity(self, vec1, vec2):
        return cosine_similarity([vec1], [vec2])[0][0]

    def find_most_similar_movies(self, user_input_vector, movie_vectors):
        similarity_scores = {
            movie_id: self.calculate_cosine_similarity(user_input_vector, movie_vector)
            for movie_id, movie_vector in movie_vectors
        }
        most_similar_movies = sorted(
            similarity_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]
        return most_similar_movies
