import requests
import urllib.request
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_url(url):
    time.sleep(5)
    return(requests.get(url))


if __name__ == '__main__':
    driver = webdriver.Chrome()
    dep_cities = ['北京', '上海', '广州', '深圳', '天津', '杭州', '南京', '济南', '重庆', '青岛', '大连', '宁波', '厦门', '成都',
                  '武汉', '哈尔滨', '沈阳', '西安', '长春', '长沙', '福州', '郑州', '石家庄', '苏州', '佛山', '烟台', '合肥', '昆明',
                  '唐山', '乌鲁木齐', '兰州', '呼和浩特', '南通', '潍坊', '绍兴', '邯郸', '东营', '嘉兴', '台州', '江阴', '金华',
                  '鞍山', '襄阳', '南阳', '岳阳', '漳州', '淮安', '湛江', '柳州', '绵阳']
    for dep in dep_cities:
        strhtml = get_url('https://m.dujia.qunar.com/golfz/sight/arriveRecommend?dep=' + urllib.request.quote(dep) +
                          '&exclude=&extensionImg=255,175')
        arrive_dict = strhtml.json()
        for arrive_item in arrive_dict['data']:
            for arrive_item_1 in arrive_item['subModules']:
                for query in arrive_item_1['items']:
                    driver.get('https://fh.dujia.qunar.com/?tf=package')
                    WebDriverWait(driver, 10).until((EC.presence_of_element_located(By.ID, "depCity")))
                    driver.find_element_by_xpath("//*[@id='depCity']").clear()
                    driver.find_element_by_xpath("//*[@id='depCity']").send_keys(dep)
                    driver.find_element_by_xpath("//*[@id='depCity']").send_keys(query["query"])
                    driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div[3]/div/div[2]/div/a").click()
                    print("dep:%s arr:%s" % (dep, query["query"]))
                    for i in range(100):
                        time.sleep(random.uniform(5, 6))
                        pageBtns = driver.find_element_by_xpath("html/body/div[2]/div[2]/div[0]")
                        if pageBtns == []:
                            break
                        routes = driver.find_element_by_xpath("html/body/div[2]/div[2]/div[7]/div[2]/div")
                        for route in routes:
                            result = {
                                'date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                                'dep': dep,
                                'arrive': query['query'],
                                'result': route.text
                            }
                            print(result)
                        if i < 9:
                            btns = driver.find_element_by_xpath("html/body/div[2]/div[2]/div[8]/div/div/a")
                            for a in btns:
                                if a.text == u"下一页":
                                    a.click()
                                    break
                driver.close()
