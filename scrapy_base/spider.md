# scrapy中spiders的用法详解
##1.scrapy.spider
Spider是最简单的spider，每个其他spider必须继承自该类
###1.1 name
定义spdier名字的字符串，必须且唯一
###1.2 alllowed_domains
可选，包含了spider允许爬取的域名（domain）列表（list）。
当offsiteMiddlename启用时，域名不在列表中的URL不会被跟进。
###1.3 start_urls
url列表。当没有制定特定的URL时，spider将从该列表中开始进行爬取。因此，第一个被获取的页面
的URL将是改列表之一。后续的URL将会从获取到的数据中提取。
###1.4 custom_settings
该设置将会覆盖项目级的设置
###1.5 crawler
该属性在初始化class后，由类方法from_crawler()设置。
###1.6 settings
运行过的spider设置
###1.7 logger
###1.8 from_crawler
类方法。通过这个类拿到全局设置
###1.9 start_requests
该方法必须返回一个可迭代对象。该对象包含了spider用于爬取的第一个Request。
该方法的默认实现是使用start_urls的url生成Request
###1.10 make_requests_from_url
该方法接受一个URL并返回用于爬取的Request对象。该方法在初始化request时被start_requests()
调用，也被用于转化url为request
###1.11 parse
当response没有指定回调函数时，该方法时scrapy处理下载的response的默认方法
###1.12 log
使用scrapy.log.msg()方法记录log(message)。log中自动带上该spider的name属性
###1.13 closed
当spider关闭时，该函数被调用。该方法提供了一个替代调用signals.connect()来监听spider_closed信号的快捷方式。
##2.通用spdier
###2.1 crawlerspider 
爬取一般网站常用的spider，除了从spider继承过来的属性外，其提供了一个新的属性
- rules：一个包含一个（或多个）Rule对象的集合
- parse_start_url：当start_url的请求返回时，该方法被调用。该方法分析最初的返回值并必须返回一个Item对象
或者一个Request对象或者一个可迭代的包含二者对象。
####2.1.1 爬取规则
- link_extractor：定义了如何从爬取到的页面提取链接
- callback
- cb_kwargs:包含传递给回调函数的参数的字典
- follow：布尔值，指定了根据该规则从response提取的链接是否需要跟进
- process_links：是一个callable的string，从link_extractor中获取到链接列表时将会调用到该函数，该方法主要用来过滤。
- process_request：是一个callable的string。该规则提取到每个request时都会调用该函数。该函数必须返回一个request或者None。
###2.2 XMLFeedSpider
XMLFeedspider被设计用于通过迭代各个节点来分析XML源
- iterator：用于确定使用哪个迭代器的string，可选项有：iternodes，HTML，xml
- itertag：一个包含开始迭代的节点名的string
- namespaces：一个由（prefix，url)元祖（tuple）所组成的list，其定义了在该文档中会被spider处理的可用的namespace
###2.3 CSVFeedSpider
该spider除了其按行遍历而不是节点之外其他和XMLFeedSpider十分相似。
- delimiter：在csv文件中用于区分字段的分隔符，类型为string，默认为','
- headers：在csv文件中包含的用来提取字段的行的列表
- parse_row：该方法接收一个response对象及一个以提供或检测出来的header为键的字典。