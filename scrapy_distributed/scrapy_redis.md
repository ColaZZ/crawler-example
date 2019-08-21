# Scrapy分布式原理及Scrapy-redis源码解析
##1. Scrapy单机架构
- 实质上是在本机维护一个爬取队列，Scheduler进行调度
- 爬取队列：Requests队列，每台主机分别维护
- 调度器：负责从队列中调度Requests进行爬取
##2.分布式爬虫架构
###2.1 多台主机协作的关键
共享爬取队列
###2.2 分布式爬虫框架
- Queue：共享队列，统一的爬取规则，多台主机共享
- 多台Schedule：调度器，各台主机的调度器统一从Queue调度
- Master：主机，维护爬取队列Request
- Slave：从机，负责数据抓取，数据处理，数据存储，维护调度器
###2.3 队列用什么维护？
- Redis队列
- 非关系型数据库，key-value形式存储结构灵活
- 是内存中的数据结构存储系统，处理速度快，性能好
- 提供队列，集合等多种存储结构，方便队列维护
###2.4 怎样来去重
- Redis集合
- Redis提供集合数据结构，在Redis集合中存储每个Request的指纹
- 在向Request队列中加入Request前首先验证这个Request的指纹是否已经加入集合中
- 如果已经存在，则不添加Request到队列，如果不存在，则将Request添加入队列并将指纹加入集合
###2.5 怎样防止中断
- 从机启动时判断
- 在每台从机Scrapy启动时都会判断，当前Redis中Request队列是否为空
- 如果不为空，则从队列中取得下一个Request执行爬取
- 如果为空，则重新开始爬取，第一台从机执行爬取向队列中添加Request
###2.6 怎样实现该架构？
- Scrapy-Redis库实现了如上架构，改写了Scrapy的调度器，队列等组件，利用它可以方便地实现Scrapy分布式架构
##3. Scrapy-Redis详解
###3.1 scrapy_redis.scheduler.py（调度器）
```python
class Scheduler(object):
    """Redis-based scheduler

    Settings
    --------
    SCHEDULER_PERSIST : bool (default: False)
        Whether to persist or clear redis queue.
    SCHEDULER_FLUSH_ON_START : bool (default: False)
        Whether to flush redis queue on start.
    SCHEDULER_IDLE_BEFORE_CLOSE : int (default: 0)
        How many seconds to wait before closing if no message is received.
    SCHEDULER_QUEUE_KEY : str
        Scheduler redis key.
    SCHEDULER_QUEUE_CLASS : str
        Scheduler queue class.
    SCHEDULER_DUPEFILTER_KEY : str
        Scheduler dupefilter redis key.
    SCHEDULER_DUPEFILTER_CLASS : str
        Scheduler dupefilter class.
    SCHEDULER_SERIALIZER : str
        Scheduler serializer.

    """

    def __init__(self, server,
                 persist=False,
                 flush_on_start=False,
                 queue_key=defaults.SCHEDULER_QUEUE_KEY,
                 queue_cls=defaults.SCHEDULER_QUEUE_CLASS,
                 dupefilter_key=defaults.SCHEDULER_DUPEFILTER_KEY,
                 dupefilter_cls=defaults.SCHEDULER_DUPEFILTER_CLASS,
                 idle_before_close=0,
                 serializer=None):
        """Initialize scheduler.

        Parameters
        ----------
        server : Redis
            这是Redis实例
        persist : bool
            是否在关闭时清空Requests.默认值是False。
        flush_on_start : bool
            是否在启动时清空Requests。 默认值是False。
        queue_key : str
            Request队列的Key名字
        queue_cls : str
            队列的可导入路径（就是使用什么队列）
        dupefilter_key : str
            去重队列的Key
        dupefilter_cls : str
            去重类的可导入路径。
        idle_before_close : int
            等待多久关闭

        """
        if idle_before_close < 0:
            raise TypeError("idle_before_close cannot be negative")

        self.server = server
        self.persist = persist
        self.flush_on_start = flush_on_start
        self.queue_key = queue_key
        self.queue_cls = queue_cls
        self.dupefilter_cls = dupefilter_cls
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.serializer = serializer
        self.stats = None

    def __len__(self):
        return len(self.queue)

    @classmethod
    def from_settings(cls, settings):
        kwargs = {
            'persist': settings.getbool('SCHEDULER_PERSIST'),
            'flush_on_start': settings.getbool('SCHEDULER_FLUSH_ON_START'),
            'idle_before_close': settings.getint('SCHEDULER_IDLE_BEFORE_CLOSE'),
        }

        # If these values are missing, it means we want to use the defaults.
        optional = {
            # TODO: Use custom prefixes for this settings to note that are
            # specific to scrapy-redis.
            'queue_key': 'SCHEDULER_QUEUE_KEY',
            'queue_cls': 'SCHEDULER_QUEUE_CLASS',
            'dupefilter_key': 'SCHEDULER_DUPEFILTER_KEY',
            # We use the default setting name to keep compatibility.
            'dupefilter_cls': 'DUPEFILTER_CLASS',
            'serializer': 'SCHEDULER_SERIALIZER',
        }
        # 从setting中获取配置组装成dict(具体获取那些配置是optional字典中key)
        for name, setting_name in optional.items():
            val = settings.get(setting_name)
            if val:
                kwargs[name] = val

        # Support serializer as a path to a module.
        if isinstance(kwargs.get('serializer'), six.string_types):
            kwargs['serializer'] = importlib.import_module(kwargs['serializer'])
                # 或得一个Redis连接
        server = connection.from_settings(settings)
        # Ensure the connection is working.
        server.ping()

        return cls(server=server, **kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        # FIXME: for now, stats are only supported from this constructor
        instance.stats = crawler.stats
        return instance

    def open(self, spider):
        self.spider = spider

        try:
              # 根据self.queue_cls这个可以导入的类 实例化一个队列
            self.queue = load_object(self.queue_cls)(
                server=self.server,
                spider=spider,
                key=self.queue_key % {'spider': spider.name},
                serializer=self.serializer,
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

        try:
              # 根据self.dupefilter_cls这个可以导入的类 实例一个去重集合
            # 默认是集合 可以实现自己的去重方式 比如 bool 去重
            self.df = load_object(self.dupefilter_cls)(
                server=self.server,
                key=self.dupefilter_key % {'spider': spider.name},
                debug=spider.settings.getbool('DUPEFILTER_DEBUG'),
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate dupefilter class '%s': %s",
                             self.dupefilter_cls, e)

        if self.flush_on_start:
            self.flush()
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        if not self.persist:
            self.flush()

    def flush(self):
        self.df.clear()
        self.queue.clear()

    def enqueue_request(self, request):
      """这个和Scrapy本身的一样"""
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return False
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        # 向队列里面添加一个Request
        self.queue.push(request)
        return True

    def next_request(self):
      """获取一个Request"""
        block_pop_timeout = self.idle_before_close
        # block_pop_timeout 是一个等待参数 队列没有东西会等待这个时间  超时就会关闭
        request = self.queue.pop(block_pop_timeout)
        if request and self.stats:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def has_pending_requests(self):
        return len(self) > 0
```
###3.2 scrapy_redis.queue.py（队列）
```python
class PriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""
        """其实就是使用Redis的有序集合 来对Request进行排序，这样就可以优先级高的在有序集合的顶层 我们只需要"""
    """从上往下依次获取Request即可"""
    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        """添加一个Request进队列"""
        # self._encode_request 将Request请求进行序列化
        data = self._encode_request(request)
        """
        d = {
        'url': to_unicode(request.url),  # urls should be safe (safe_string_url)
        'callback': cb,
        'errback': eb,
        'method': request.method,
        'headers': dict(request.headers),
        'body': request.body,
        'cookies': request.cookies,
        'meta': request.meta,
        '_encoding': request._encoding,
        'priority': request.priority,
        'dont_filter': request.dont_filter,
        'flags': request.flags,
        '_class': request.__module__ + '.' + request.__class__.__name__
            }

        data就是上面这个字典的序列化
        在Scrapy.utils.reqser.py 中的request_to_dict方法中处理
        """

        # 在Redis有序集合中数值越小优先级越高(就是会被放在顶层)所以这个位置是取得 相反数
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        # ZADD 是添加进有序集合
        self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        有序集合不支持超时所以就木有使用timeout了  这个timeout就是挂羊头卖狗肉
        """
        """从有序集合中取出一个Request"""
        # use atomic range/remove using multi/exec
        """使用multi的原因是为了将获取Request和删除Request合并成一个操作(原子性的)在获取到一个元素之后 删除它，因为有序集合 不像list 有pop 这种方式啊"""
        pipe = self.server.pipeline()
        pipe.multi()
        # 取出 顶层第一个
        # zrange :返回有序集 key 中，指定区间内的成员。0,0 就是第一个了
        # zremrangebyrank：移除有序集 key 中，指定排名(rank)区间内的所有成员 0，0也就是第一个了
        # 更多请参考Redis官方文档
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])
```
###3.3scrapy_redis.dupefilter.py（去重）
```python
def request_seen(self, request):
  """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
  # 通过self.request_fingerprint 会生一个sha1的指纹
  fp = self.request_fingerprint(request)
  # This returns the number of values added, zero if already exists.
  # 添加进一个Redis集合如果self.key这个集合中存在fp这个指纹会返回1  不存在返回0
  added = self.server.sadd(self.key, fp)
  return added == 0
```


