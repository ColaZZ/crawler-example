#scrapy框架基本使用
##1.目标站点分析
官方提供网站http://quotes.toscrape.com/
翻页数据 GET /page/1    (GET页数即可)
##2.流程框架
###1.抓取第一页
请求第一页的URL并得到源代码，进行下一步分析
###2.获取内容和下一页链接
分析源代码，提取首页内容，获取下一页链接等待进一步爬取
###3.翻页爬取
请求下一页信息，分许内容并请求再下一页链接
###4.保存爬取结果
将爬取内容保存为特定格式如文本、数据库
##3.爬虫实战
```bash
scrapy startproject quotetutorial
cd quotetutorial
scrapy genspider quotes quotes.toscrape.com

```


小坑：
```pymongo.errors.ServerSelectionTimeoutError: localhsot:27017: [Errno 8] nodename nor servname provide```

将localhost改成127.0.0.1即可