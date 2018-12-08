import pymysql as pm

USER = 'root'
PASSWORD = '8kNEEb8w'
NAME = 'rutul_concord'


class Database:
    def __init__(self):
        self._connection = pm.connect(user=USER, password=PASSWORD, db=NAME, charset='utf8')

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
