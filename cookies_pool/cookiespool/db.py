import redis
import random
from .config import *
from .error import *


class RedisClient(object):
    def __init__(self, host=REDIS_HOST,port=REDIS_PASSWORD,password=REDIS_PASSWORD):
        """
        初始化Redis
        """
        if password:
            self._db = redis.Redis(host=host, port=port, password=password)
        else:
            self._db = redis.Redis(host=host, port=port)
        self.domain = REDIS_DOMAIN
        self.name = REDIS_NAME

    def _key(self, key):
        """
        得到格式化的key
        :param key: 最后一个key
        :return:
        """
        return "{domain}:{name}:{key}".format(domain=self.domain, name=self.name, key=key)

    def get(self, key):
        """
        根据键名获取键值对
        :param key:
        :param value:
        :return:
        """
        raise NotImplemented

    def set(self, key, value):
        """
        设置键值对
        :param key:
        :param value:
        :return:
        """
        raise NotImplemented

    def delete(self, key):
        """
        根据键值删除键值对
        :param key:
        :return:
        """
        raise NotImplemented

    def keys(self):
        """
        得到所有的键名
        :return:
        """
        return self._db.keys("{domain}:{name}:*".format(domain=self.domain, name=self.name))

    def flush(self):
        """
        清空数据库，慎用
        :return:
        """
        self._db.flushall()


class CookiesRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='cookies', name='default'):
        """
        管理Cookies的对象
        :param host:
        :param port:
        :param password:
        :param domain:
        :param name:
        """
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name

    def set(self, key, value):
        try:
            self._db.set(self._key(key), value)
        except:
            raise SetCookieError

    def get(self, key):
        try:
            self._db.get(self._key(key)).decode('utf-8')
        except:
            return None

    def delete(self, key):
        try:
            print('delete ')
            self._db.delete(self._key(key))
        except:
            raise DeleteCookieError

    def random(self):
        """
        随机得到一个cookies
        :return:
        """
        try:
            keys = self.keys()
            return self._db.get(random.choice(keys))
        except:
            raise GetRandomCookieError

    def all(self):
        """
        所有的cookies，以字典形式返回
        :return:
        """
        try:
            for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain,name=self.name)):
                group = key.decode('utf-8').split(':')
                if len(group) == 3:
                    username = group[2]
                    yield {
                        'username': username,
                        'cookies': self.get(username)
                    }
        except Exception as e:
            print(e.args)
            raise GetAllCookiesError

    def count(self):
        """
        根据键获取键值
        :return:
        """
        return len(self.keys())


class AccountRedisClient(RedisClient):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, domain='account', name='dedault'):
        RedisClient.__init__(self, host, port, password)
        self.domain = domain
        self.name = name

    def set(self, key, value):
        try:
            return self._db.set(self._key(key), value)
        except:
            raise SetAccountError

    def get(self, key):
        try:
            return self._db.get(self._key(key))
        except:
            raise GetAccountError

    def all(self):
        """

        :return:
        """
        try:
            for key in self._db.keys('{domain}:{name}:*'.format(domain=self.domain, name=self.name)):
                group = key.decode('utf-8').split(':')
                if len(group) == 3:
                    username = group[2]
                    yield {
                        'username': username,
                        'cookies': self.get(username)
                    }
        except Exception as e:
            print(e.args)
            raise GetAllAccountError

    def delete(self, key):
        try:
            return self._db.delete(self._key(key))
        except:
            raise DeleteAccountError


if __name__ == '__main__':
    """
    conn = CookiesRedisClient()
    conn.set('name', 'Mike')
    conn.set('name2', 'Bob')
    conn.set('name3', 'Amy')
    print(conn.get('name'))
    conn.delete('name')
    print(conn.keys())
    print(conn.random())
    """
    # 测试
    conn = AccountRedisClient(name='weibo')
    conn2 = AccountRedisClient(name='mweibo')

    accounts = conn.all()
    for account in accounts:
        conn2.set(account['username'], account['password'])

