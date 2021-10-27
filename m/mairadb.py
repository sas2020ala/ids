"""
Module for working with a database
"""
import pickle

import redis
import mariadb as dbm

from m.md import a_db, a_cache
from m.mgr import System


class Database:

    def __init__(self):
        self.con = None
        self.pool = None
        self.dc = None
        self.schema = 'ids'

    def connect(self):
        try:
            dat = self.dsn()
            self.con = dbm.connect(
                user=dat['model'],
                password=dat['password'],
                host=dat['host'],
                port=int(dat['port']),
                database=dat['database']
            )

        except Exception as e:
            System.crash(f"db.connect: {e}")

    def check(self):
        try:
            self.con.ping()
        except Exception as e:
            try:
                self.con.reconnect()
            except Exception as e:
                System.crash(f"db.check: {e}")
        return self.con

    def close(self):
        if self.con:
            self.con.close()

    def commit(self):
        if self.con:
            self.con.commit()

    def rollback(self):
        con = self.check()
        if con:
            con.rollback()

    def connect_to_cache(self):
        """
        Connect to redis
        :return dc: redis connection object
        """

        with open(a_cache, 'r') as fp:
            # hostname:port:database:username:password
            vs = fp.readline().strip().split(':')
            p = {"host": vs[0], "port": vs[1], "db": vs[2], "password": vs[3]}

        if vs:
            try:
                self.dc = redis.Redis(**p)
            except Exception as e:
                System.crash(f"db.connect_to_cache: {e}")

        else:
            System.crash(f"db.connect_to_cache: invalid parameters")

    def save_to_cache(self, k: str, obj: any):
        """
        Data save to data cache, etc, redis, memcache
        :param k: key
        :param obj: python object
        """
        d = pickle.dumps(obj)

        if self.dc.ping():
            self.dc.set(k, d)

        else:
            self.connect_to_cache()

            if self.dc:
                self.dc.set(k, d)

            else:
                System.crash(f"db.save_to_cache: connection error")

    def get_from_cache(self, k: str):
        if __debug__:
            print(f"   database.get_from_cache: {k}")
        """
        Get data from cache, etc, redis, memcache
        :param k: key
        """

        if self.dc.ping():
            d = pickle.loads(self.dc.get(k))

        else:
            self.connect_to_cache()
            d = pickle.loads(self.dc.get(k))

        return d

    @staticmethod
    def dsn(typ=0):
        """
        Get DSN(bpd source name) parameters from .db file

        :param typ: result type: 0 - dict, 1 - string
        :return: DSN for connection to database
        """

        fmt: list = ['host', 'port', 'database', 'model', 'password']

        with open(a_db, 'r') as fp:
            # hostname:port:database:username:password
            vs = fp.readline().strip().split(':')

            if typ == 0:
                d = {fmt[j]: int(vs[j]) if fmt[j] == 'port' else vs[j] for j in range(5)}

            elif typ == 1:
                d = ' '.join([f'{fmt[j]}={vs[j]}' for j in range(5)])

            else:
                d = None

        return d
