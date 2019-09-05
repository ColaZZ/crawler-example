# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
#
# 用于保存抓取的数据的容器，其储存方式类似于Python的字典
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

class StockstarItemLoader(ItemLoader): #用于存储爬虫所抓取的字段内容
    default_output_processor = TakeFirst()
class StockstarItem(scrapy.Item):#建立相应的字段
    #default the fields for you item here like:
    #name = scrapy.Field()
    code = scrapy.Field()  #股票代码
    abbr = scrapy.Field()  #股票简称
    last_trade = scrapy.Field()  #最新价
    chg_ratio = scrapy.Field()   #涨跌幅
    chg_amt = scrapy.Field()     #涨跌额
    chg_ratio_5min = scrapy.Field()  #5分钟涨幅
    volumn = scrapy.Field()  #成交量
    turn_over = scrapy.Field()  #成交额
