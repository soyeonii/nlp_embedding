import requests
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='1234', db='nlp_movie_data', charset='utf8')
curs = conn.cursor()

url = "https://api.themoviedb.org/3/movie/popular?language=ko-KR&page="

headers = {
    "accept": "application/json",
    "Authorization": "Bearer AUTH_KEY"
}

page = 1
while True:
    response = requests.get(url + str(page), headers=headers)

    if response.status_code == 200:
        data = response.json()

        if not data['results']:
            break

        for movie in data['results']:
            if movie['overview']:
                print(movie['title'])

                sql = 'INSERT INTO movies (title, poster_path, release_date) VALUES (%s, %s, %s)'
                curs.execute(sql, (movie['title'], movie['poster_path'], movie['release_date']))

                sql = 'INSERT INTO movie_plots (movie_id, plot) VALUES (%s, %s)'
                curs.execute(sql, (curs.lastrowid, movie['overview']))

        conn.commit()
        page += 1
    else:
        print("API 요청에 실패했습니다.")

curs.close()
conn.close()