# Scrapy分布式原理及Scrapy-redis源码解析
##1. Scrapy单机架构
- 实质上是在本机维护一个爬取队列，Scheduler进行调度
- 爬取队列：Requests队列，每台主机分别维护
- 调度器：负责从队列中调度Requests进行爬取