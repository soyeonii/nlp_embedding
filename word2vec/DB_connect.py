import pymysql


class DB_connect:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            db="movie_data",
            charset="utf8",
        )
        self.curs = self.conn.cursor()

    def select(self, sql):
        self.curs.execute(sql)
        data = self.curs.fetchall()
        return data

    def insert(self, sql, data):
        self.curs.execute(sql, data)
        self.conn.commit()

    def close(self):
        self.curs.close()
        self.conn.close()
