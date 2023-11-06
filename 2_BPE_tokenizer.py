from transformers import GPT2Tokenizer
from kss import split_sentences
import pymysql
import os

tokenizer_gpt = GPT2Tokenizer.from_pretrained(os.getcwd() + "/bbpe")
tokenizer_gpt.pad_token = "[PAD]"

conn = pymysql.connect(host='localhost', user='root', password='1234', db='nlp_movie_data', charset='utf8')
curs = conn.cursor()

sql = "SELECT movie_id, plot FROM movie_plots"
curs.execute(sql)
plots = curs.fetchall()

for plot in plots:
    sentences = split_sentences(plot[1])
    print(sentences)
    
    tokenized_sentences = [tokenizer_gpt.tokenize(sentence) for sentence in sentences]
    print(tokenized_sentences)

    for tokenized_sentence in tokenized_sentences:
        text = ' '.join(tokenized_sentence)
        sql = "INSERT INTO movie_plot_tokens (movie_id, plot_token) VALUES (%s, %s)"
        curs.execute(sql, (plot[0], text))
        conn.commit()

    # batch_inputs = tokenizer_gpt(
    #     sentences,
    #     padding="max_length",
    #     max_length=20,
    #     truncation=True
    # )
    # print(batch_inputs)

curs.close()
conn.close()