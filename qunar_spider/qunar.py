import requests
import urllib.request
import time
import pymongo

client = pymongo.MongoClient('localhost', 27017, connect=False)
book_qunar = client['qunar']
sheet_qunar_zyx = book_qunar['qunar_zyx']


def savetomongo(result):
    """
    保存到mongodb数据库
    :param result: 出发城市到目的城市自由行搜索结果
    :return:
    """
    sheet_qunar_zyx.insert_one(result)


def begin():
    """
    获取去哪儿网出发地站点列表
    :return:
    """
    depurl='https://touch.dujia.qunar.com/depCities.qunar'
    response=requests.get(depurl)
    deps=response.json()
    for dep_item in deps['data']:
        for dep in deps['data'][dep_item]:
            yield dep#出发城市


def get_list(dep , item):
    """
    获取产品列表信息
    :param dep: 出发地
    :param item: 目的地
    :return:
    """
    url = 'https://touch.dujia.qunar.com/list?modules=list%2CbookingInfo%2CactivityDetail&dep={}&query={}&dappDealTrace=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&it=FreetripTouchin&date=&configDepNew=&needNoResult=true&originalquery={}&limit=0,28&includeAD=true&qsact=search'.format(
        urllib.request.quote(dep), urllib.request.quote(item), urllib.request.quote(item))
    time.sleep(1)
    strhtml = requests.get(url)

    try:
        routeCount = int(strhtml.json()['data']['limit']['routeCount'])
    except:
        return

    for limit in range(0, routeCount, 20):
        url = 'https://touch.dujia.qunar.com/list?modules=list%2CbookingInfo%2CactivityDetail&dep={}&query={}' \
              '&dappDealTrace=false&mobFunction=%E6%89%A9%E5%B1%95%E8%87%AA%E7%94%B1%E8%A1%8C&cfrom=zyx&' \
              'it=FreetripTouchin&date=&configDepNew=&needNoResult=true&originalquery={}&limit={},28&' \
              'includeAD=true&qsact=search'.format(urllib.request.quote(dep), urllib.request.quote(item),
                                                   urllib.request.quote('item'), limit)
        time.sleep(1)
        strhtml = requests.get(url)
        result = {
            'data': time.strftime('%Y-%m-%d', time.localtime(time.time())),
            'dep': dep,
            'arrive': item,
            'limit': limit,
            'result': strhtml.json()
        }
        savetomongo(result)


def get_json(url):
    strhtml = requests.get(url)
    time.sleep(1)
    return strhtml.json()


def get_all_data(dep):
    a = []
    url = 'https://touch.dujia.qunar.com/golfz/sight/arriveRecommend?dep={}&exclude=&extensionImg=255,175'.format(
        urllib.request.quote(dep))
    arrive_dict = get_json(url)
    for arr_item in arrive_dict['data']:
        for arr_item_1 in arr_item['subModules']:
            for query in arr_item_1['items']:
                if query['query'] not in a:
                    a.append(query['query'])
    for item in a:
        get_list(dep, item)




