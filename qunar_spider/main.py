from qunar_spider.qunar import get_all_data, begin, client
from multiprocessing import Pool

if __name__ == '__main__':
    deps = begin()
    # 开启多线程
    pool = Pool()
    pool.map(get_all_data, [dep for dep in deps])
    client.close()