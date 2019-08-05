import redis
from .error import PoolEmptyError
from .settings import HOST, PORT


class RedisClient(object):
    def __int__(self, host=HOST, port=PORT):
        if PASSWORD:
            self._db = redis.Redis(host=host, port=host, password=PASSWORD)
        else:
            self._db = redis.Redis(host=host, port=port)

    def get(self, count=1):
        proxies = self._db.lrange("proxies", 0, count-1)
        self._db.ltrim("poxies", count-1)
        return proxies

    def put(self, proxy):
        """
        add proxy to right top
        :param proxy:
        :return:
        """
        self._db.rpush("proxies", proxy)

    def pop(self):
        """
        get proxy from right
        :return:
        """
        try:
            return self._db.rpop("proxies").decode("utf-8")
        except:
            raise PoolEmptyError

    @property
    def queue_len(self):
        """
        get lenght from queue
        :return:
        """
        return self._db.llen('proxies')

    def flush(self):
        """
        flush db
        """
        self._db.flushall()


if __name__ == '__main__':
    conn = RedisClient()
    print(conn.pop())


