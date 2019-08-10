# Scrapy命令行详解
##1.使用scrapy工具
###1.1创建项目
```bash
scrapy startproject myproject
```
###1.2控制项目
比如创建一个新的spider
```bash
scrapy genspider mydomain mydomain.com
```
##2.可用的工具命令
###2.1全局命令
####1.startproject
创建项目
####2.settings
获取Scrapy的设定
```bash
scrapy settings --get BOT_NAME
```
####3.runspider
在未创建项目的情况下，运行一个编写在Python文件中的spider。
```bash
scrapy runspider myspider.py
```
####4.shell
以给定的URL(如果给出)或者空(没有给出URL)启动Scrapy shell。
```bash
scrapy shell http://www.example.com/some/page.html
```
####5.fetch
使用Scrapy下载器(downloader)下载给定的URL，并将获取到的内容送到标准输出。
```bash
scrapy fetch --nolog --headers http://www.example.com/
```
####6.view
在浏览器中打开给定的URL，并以Scrapy spider获取到的形式展现。 有些时候spider获取到的页面和普通用户看到的并不相同。 因此该命令可以用来检查spider所获取到的页面，并确认这是您所期望的。
```bash
scrapy view http://www.example.com/some/page.html
```
####7.version
输出Scrapy版本。配合 -v 运行时，该命令同时输出Python, Twisted以及平台的信息，方便bug提交。
###2.2项目命令
####1.crawl
使用spider进行爬取。
```bash
scrapy crawl myspider
```
####2.check
运行contract检查。
```bash
scrapy check
```
####3.list
列出当前项目中所有可用的spider。每行输出一个spider。
```bash
$ scrapy edit spider1
```
####4.edit
使用 EDITOR 中设定的编辑器编辑给定的spider
```bash
$ scrapy edit spider1
```
####5.parse
获取给定的URL并使用相应的spider分析处理。如果您提供 --callback 选项，则使用spider的该方法处理，否则使用 parse 。
* --spider=SPIDER: 跳过自动检测spider并强制使用特定的spider
* --a NAME=VALUE: 设置spider的参数(可能被重复)
* --callback or -c: spider中用于解析返回(response)的回调函数
* --pipelines: 在pipeline中处理item
* --rules or -r: 使用 CrawlSpider 规则来发现用来解析返回(response)的回调函数
* --noitems: 不显示爬取到的item
* --nolinks: 不显示提取到的链接
* --nocolour: 避免使用pygments对输出着色
* --depth or -d: 指定跟进链接请求的层次数(默认: 1)
* --verbose or -v: 显示每个请求的详细信息
```bash
scrapy parse http://www.example.com/ -c parse_item
```
####6.genspider
在当前项目中创建spider。
```bash
$ scrapy genspider -l
```
####7.deploy
将项目部署到Scrapyd服务。
```bash
$ scrapy deploy [ <target:project> | -l <target> | -L ]
```
####8.bench
运行benchmark测试
```bash
$ scrapy bench 
```


