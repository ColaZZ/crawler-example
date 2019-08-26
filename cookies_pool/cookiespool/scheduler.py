import time
from multiprocessing import Process
from .config import *


class Scheduler(object):
    # 验证器
    @staticmethod
    def valid_cookie():
        # while True:
        #     print("Checking Cookies")
        #     try：
        #         for name, cls in TESTER_MAP.items():
        #         tester =
        #     except Exception as e:
        #         print(e.args)

        pass



    # 产生器
    @staticmethod
    def generate_cookie():
        pass

    # api
    @staticmethod
    def api():
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        pass