#将爬取的数据导出到items.json文件

from scrapy.cmdline import execute
execute(["scrapy","crawl","stock","-o","items.json"])