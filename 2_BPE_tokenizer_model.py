import pymysql
from tokenizers import ByteLevelBPETokenizer
import os

conn = pymysql.connect(host='localhost', user='root', password='1234', db='nlp_movie_data', charset='utf8')
curs = conn.cursor()
sql = "SELECT plot FROM movie_plots"
curs.execute(sql)

plots = curs.fetchall()
curs.close()
conn.close()

data = [plot[0] for plot in plots]

with open("plot_data.txt", "w", encoding="utf-8") as file:
    for text in data:
        file.write(text + "\n")

bytebpe_tokenizer = ByteLevelBPETokenizer()
bytebpe_tokenizer.train(
    files=["plot_data.txt"],
    vocab_size=10000,
    special_tokens=["[PAD]"]
)

try:
    output_dir = os.getcwd() + "/bbpe"
    os.makedirs(output_dir, exist_ok=True)
    bytebpe_tokenizer.save_model(output_dir)
    print("Model saved successfully.")
except Exception as e:
    print(f"Error: {e}")