# scrapy中Download Middleware用法
下载器中间件事介于Scrapy的request/response处理的钩子框架，适用于全局修改Scrapy request和
response的一个轻量、底层的系统
##1.激活下载器中间件
要激活下载器中间件组件，将其加入到DOWNLOADER_MIDDLEWARES设置中。
##2.编写自己的下载器中间件
每个中间组件是一个定义了以下一个或多个方法的python类
```python
class scrapy.dowloadermiddlewares.DownloaderMiddleware
```
###2.1 process_request(request, spider)
- 当每个request通过下载中间件时，该方法被调用
- process_request(request, spider)必须返回其中之一：
   - None：scrapy将继续处理该request，执行其他的中间件的相应方法，直到合适的下载器处理函数（download handler）被调用
   该request被执行
   - Response对象：Scrapy将不会调用任何其他的process_request()或process_exception()方法，或相应的下载函数，将其返回该response，
   已安装的中间件的process_response()方法则会在每个response返回时被调用
   - Request对象：Scrapy停止调用，process_request()方法并重新调度返回的request。当新返回的request被执行后，相应地中间件将会被重新调度下载。
###2.2 process_response(request, reponse, spider)
   - Response对象：该Response会被在链中的其他中间件的process_response()方法处理
   - Request对象：中间链停止，返回的request会被重新调度下载。
###2.3 process_exception(request, exception, spider)
   - 当下载处理器（download handler）或process_request()(下载中间件)抛出异常（包括IgnoreRequest异常）时，Scrapy调用process_exception()
   - None：继续处理该异常，接着调用已安装的其他中间件都被调用完毕，则调用默认的异常处理
   - Response：已安装的中间件链的process_response()方法被调用，Scrapy将不会调用任何其他中间件的process_exception()方法
   - Request：返回的request将会被重新调用下载。
##3.内置下载中间件参看手册
###3.1 cookies middleware
该中间件使得爬取需要cookies（例如使用session）的网站成为了可能。其追踪了web server发送的cookie，并在之后的request中发送回去，就如浏览器所做的那样。
####3.1.1 单spider多cookie session
```cookiejar```，默认情况下其使用一个cookiejar（session）
```python
scrapy.Request("http://www.example.com/otherpage",
        meta={'cookiejar': response.meta['cookiejar']},
        callback=self.parse_other_page)
```
####3.1.2 COOOKIES_ENABLED
默认True，是否启用
####3.1.3 COOKIES_DEBUG
默认False
###3.2 DefaultHeaders.Middleware
该中间件设置DEFAULT_TIMEOUT指定的request下载超过时间
###3.3 HttpAuthMiddleware
该中间件完成某些使用HTTP认证的spider生成的请求的认证过程。在spider中启用HTTO
认证，请设置spider的http_user及http_pass属性。
###3.4 HttpCacheMiddleware
该中间件为所有HTTP request及response提供了底层缓存支持。其由cache存储后端及cache策略组成。
####3.4.1 scrapy提供了两种HTTP缓存存储后端
可以使用HTTP_STORAGE设定来修改HTTP缓存存储后端
- Filesystem storage backend（默认值）
- DBM storage backend
####3.4.2 Scrapy提供了两种缓存策略
可以使用HTTPCACHE_POLICY设定来修改HTTP缓存策略
- RFC2616策略
- Dummy策略（默认值）
####3.4.3 HTTPCACHE中间件设置
- HTTPCACHE_ENABLE:HTTP缓存是否开启
- HTTPCACHE_EXPIRATION_SECS：缓存的request的超过时间，单位为秒
- HTTPCACHE_DIR：存储（底层的）HTTP缓存的目录。如果为空，则HTTP缓存将会被关闭，如果为相对目录，则相对于项目数据目录
- HTTPCACHE_IGNORE_HTTP_CODES：不缓存设置中的HTTP返回值（code）的request
- HTTPCACHE_IGNORE_MISSING：如果启用，在缓存中没找到的request将会忽略，不下载
- HTTPCACHE_IGNORE_SCHEMES：不缓存这些URI标准（scheme）的response
- HTTPCACHE_STORAGE：实现缓存存储后端的类
- HTTPCACHE_DBM_MODULE：在DBM存储后端的数据库模块，该设定针对DBM后端
- HTTPCACHE_POLICY：实现缓存策略的类
- HTTPCACHE_GZIP：如果启用，scrapy将会使用gzip压缩所有缓存的数据，该设定只针对文件系统后端（Filesystem backend）有效
###3.5 HTTP Compression Middleware
- 该中间件提供了对压缩（gzip，defate）数据的支持
- HTTP Compression Middleware settings
   - COMPRESSION_ENALBED：默认True，compression Middleware（压缩中间件）是否开启。
###3.6 Chunked Transfer Middleware 
该中间件添加了对Chunked transfer encoding的支持
###3.7 HttpProxyMiddleware
该中间件提供了对request设置HTTP代理的支持。可以通过在Request对象中设置proxy元数据来开启代理。
###3.8 RedirectMiddleware
该中间件根据response的状态处理重定向的request，Resquest.meta的redirect_urls键找到。
- RedirectMiddleware可以通过下列设置进行配置：
   - REDIRECT_ENABLED：是否启用Redirect中间件（默认：True）
   - REDIRECT_MAX_TIMES：单个request被重定向的最大次数
###3.9 MetaRefresh Middleware
该中间件根据meta-refresh html标签处理request重定向
####3.9.1 MetaRefreshMiddleware可以通过以下设定进行配置
- METAREFRESH_ENABLED
- METAREFRESH_MAXDELAY
- 该中间件遵循RedirectMiddleware描述的REDIRECT_MAX_TIMES设定，dont_redirect及redirect_urls meta key。
####3.9.2 Meta Refresh Middleware settings
- METAREFRESH_ENABLED：默认True，meta Refresh中间件是否启用
- REDIRECT_MAX_METAREFRESH_DELAY：默认100，跟进重定向的最大meta-fresh延迟（单位：秒）
###3.10 RetryMiddleware
该中间件将重试可能由于临时的问题，例如连接超时或者HTTP 500错误导致失败的页面
####3.10.1 RetryMiddleware可以通过下列设定进行配置：
- RETRY_ENALBED
- RETRY_TIMES
- RETRY_HTTP_CODES
####3.10.2 RetryMiddleware settings
- RETRY_ENABLED：默认True，是否启用
- RETRY_TIMES：默认2，包括第一次下载，最多的重试次数
- RETRY_HTTP_CODES：默认[500, 502, 503, 504, 400, 408],重试的response的返回值（code）。
其他错误（DNS查找问题，连接失败及其他）则一定会进行重试。
###3.11 RobotsTxtMiddleware
该中间件过滤所有robots.txt eclusion standard中禁止的request，确认该中间件及ROBOTSTXT_OBEY设置被弃用以确保Scrapy遵守robots.txt
###3.12 Downloader Stats
保存所有通过的request.response及exception的中间件，您必须启用DOWNLOADER_STATS来启用该中间件
###3.13 User Agent Middleware
用于覆盖spider的默认user_agent的中间件，要使得spider能覆盖默认的user_agent，其user_agent属性必须被设置
###3.14 AjaxCrawlerMiddleware
####3.14.1 根据meta-fragment html标签，AJAX可爬取页面的中间件
####3.14.2 AjaxCrawlMiddleware设置
- AjaxCRAWL_ENABLED：默认false，是否启用

