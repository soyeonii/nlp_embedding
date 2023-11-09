# -*- coding: utf-8 -*-

import openai
import numpy as np
import pymysql

conn = pymysql.connect(
    host="localhost", user="root", password="1234", db="nlp_movie_data", charset="utf8"
)
curs = conn.cursor()

openai.api_key = "OPENAI_API_KEY"


sql = "SELECT movie_id, GROUP_CONCAT(plot_token) AS concatenated_tokens FROM movie_plot_tokens GROUP BY movie_id"
curs.execute(sql)
tokens = curs.fetchall()

for token in tokens:
    response = openai.Embedding.create(model="text-embedding-ada-002", input=token[1])

    result = np.mean(np.array(response.data[0].embedding))
    print(token[0], result)

    sql = "INSERT INTO movie_plot_embedding (movie_id, plot_embedding) VALUES (%s, %s)"
    curs.execute(sql, (token[0], result))
    tokens = curs.fetchall()

conn.commit()

curs.close()
conn.close()
