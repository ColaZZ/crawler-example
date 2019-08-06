#1.命令行接口
##1.Global Config全局配置
###1.--config
启动时配置文件
##2.all
运行所有的组件
##3.bench
请求页测试
#2.API
##1.self.crawl
###参数
####1.url
####2.callback  回调函数
####3.age   过期时间
####4，priority  优先级
####5.exetime   执行时间
####6.retries   重试次数，默认为3
####7.itag      标志符
####8.auto_recrawl  自动重新爬取  
####9.method    HTTP的方法（GET，POST...）
####10.params   get请求的参数
####11.data     post提交用的data    
####12.files    上传的文件
####13.user_agent      
####14.headers      
####15.cookies
####16，connect_timeout      链接的超时时间
####17.timeout               请求的超时时间
####18.alllow_redirect       允许重定向      
####19.validate_cert         证书错误          
####20.proxy                  代理
####21.etag                  当前页面是否发生变化
####22.last_modified        
####23.fetch_type           
####24.js_script            网页完成之后执行JS脚本
####25.load_images          是否加载图片
####26.save                 多个函数之间传递变量的参数

##2.Response
###1.Response.url       请求的url
###2.Response.text      网页的源代码
###3.Response.content   网页的二进制数据
###4.Response.doc       用于网页解析
###5.Response.etree     
###6.Response.json
###7.Response.status_code   状态码
###8.Response.time
###9.Response.ok
###10.Response.encoding
###11.Response.save     不同的函数之间传递参数

##3.self.send_message

##4，every(minutes=0,seconds=0)
     
