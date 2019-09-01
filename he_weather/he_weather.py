import requests
import time
import pymongo

client = pymongo.MongoClient('localhost', 27017)
book_weather = client['weather']
sheet_weather = book_weather['sheet_weather_3']

dic = {}
url = "https://cdn.heweather.com/china-city-list.txt"
strhtml = requests.get(url)
strhtml.encoding = "utf-8"
data = strhtml.text

data1 = data.split("\n")

for i in range(6):
    data1.remove(data1[0])

for item in data1:
    url = "https://free-api.heweather.net/s6/weather/forecast?location=" + str(item[2:13]) +"&key=91fc049f7db24740a61cea29400aa29e"
    html = requests.get(url)
    html.encoding = "utf-8"
    time.sleep(1)
    dic = html.json()

    sheet_weather.insert_one(dic)

    # for item in dic['HeWeather6'][0]['daily_forecast']:
    #     # print(item["tmp"]["max"])
    #     print(item["tmp_max"])


