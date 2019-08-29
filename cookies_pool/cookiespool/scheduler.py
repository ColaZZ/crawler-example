import time
from multiprocessing import Process
from .config import *
from .generator import *
from .tester import *
from .api import app


class Scheduler(object):
    # 验证器
    @staticmethod
    def valid_cookie(cycle=CYCLE):
        while True:
            print('Checking Cookies')
            try:
                for name, cls in TESTER_MAP.items():
                    tester = eval(cls + '(name="' + name + '")')
                    tester.run()
                    print('Tester finished')
                    del tester
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    # 产生器
    @staticmethod
    def generate_cookie(cycle=CYCLE):
        while True:
            print('Generator Cookies')
            try:
                for name, cls in GENERATOR_MAP.items():
                    generator = eval(cls + '(name="' + name + '")')
                    generator.run()
                    print('Generator Finshed')
                    generator.close()
                    print('Generator Deleted')
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    # api
    @staticmethod
    def api():
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        # 如果开关打开，依次进行生成，验证，开放Api操作
        if GENERATOR_PROCESS:
            generator_process = Process(target=Scheduler.generate_cookie())
            generator_process.start()

        if VALID_PROCESS:
            valid_process = Process(target=Scheduler.valid_cookie())
            valid_process.start()

        if API_PROCESS:
            api_process = Process(target=Scheduler.api())
            api_process.start()