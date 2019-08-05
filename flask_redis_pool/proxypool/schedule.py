# 调度器
import aiohttp
import asyncio
import time
from multiprocessing import Process
from .settings import *
from .db import *
from .getter import *
from asyncio import TimeoutError
from .error import ResourceDepletionError


class ValidityTester(object):
    test_api = TEST_API

    def __init__(self):
        self._raw_proxies = None
        self._usable_proxies = []

    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    async def test_signle_proxy(self, proxy):
        """
        test one proxy, if valid, put it to usable_proxies
        :param proxy:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf-8")
                real_proxy = 'http://' + proxy
                print('Testing', proxy)
                async with session.get(self.test_api, proxy=real_proxy, timeout=15) as reponse:
                    if reponse.status == 200:
                        self._conn.put(proxy)
                        print('Valid proxy', proxy)
            except (TimeoutError, ValueError):
                print("Invalid proxy", proxy)

    def test(self):
        """
        aio test all proxies
        :return:
        """
        print("ValidityTester is working")
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_signle_proxy(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('Async Error')


class PoolAdder(object):
    def __init__(self, thredshold):
        self._thredshold = thredshold
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._crawler = FreeProxyGetter()

    def is_over_threshold(self):
        """
        judge if count is overflow
        :return:
        """

    def add_to_queue(self):
        print('PoolAdder is working')
        proxy_count = 0
        while not self.is_over_threshold():
            for callback_label in range(self._crawler.__CrawlFuncCount__):
                callback = self._crawler.__CrawlFuncCount__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback)
                # test crawler proxies
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()
                proxy_count += len(raw_proxies)
                if self.is_over_threshold():
                    print('IP is enough, waiting to be used')
                    break
            if proxy_count == 0:
                raise  ResourceDepletionError


class Schedule(object):
    @staticmethod
    def valid_proxy(cycle=VALID_CHECK_CYCLE):
        """
        Get half of proxies which in redis
        :param cycle:
        :return:
        """
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            print('Refreshing ip')
            count = int(0.5 * conn.queue_len)
            if count == 0:
                print("Waiting for adding")
                time.sleep(cycle)
                continue
            raw_proxies = conn.get(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)

    @staticmethod
    def check_pool(lower_threadhold=POOL_LOWER_THRESHOLD,
                   upper_threadhold=POOL_UPPER_THRESHOLD,
                   cycle=POOL_LEN_CHECK_CYCLE):
        """
        If the number of proxies less than lower_threding, add proxy
        :param lower_threading:
        :param upper_threading:
        :param cycle:
        :return:
        """
        conn = RedisClient()
        adder = PoolAdder(upper_threadhold)
        while True:
            if conn.queue_len < lower_threadhold:
                adder.add_to_queue()
            time.sleep(cycle)

    def run(self):
        print("Ip processing running")
        valid_process = Process(target=Schedule.valid_proxy())
        check_process = Process(target=Schedule.check_pool())
        valid_process.start()
        check_process.start()


