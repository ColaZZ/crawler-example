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