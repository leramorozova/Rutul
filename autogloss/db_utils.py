#import pymysql as pm
import sqlite3

#USER = 'root'
#PASSWORD = '8kNEEb8w'
#NAME = 'rutul_concord'


class Database:
    def __init__(self):
        self._connection = sqlite3.connect("Rutul.db")

    def commit(self):
        self._connection.commit()

    def execute(self, q, arg):
        cur = self._connection.cursor()
        if arg != 0:
            cur.execute(q, arg)
        else:
            cur.execute(q)
        res = cur.fetchall()
        cur.close()
        return res
