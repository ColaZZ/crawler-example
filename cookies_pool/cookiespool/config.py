# 产生器默认使用的浏览器
DEFAULT_BROWSER = 'Chrome'

# 产生器类，如果扩展其他站点，请在此配置
GENERATOR_MAP = {
    'weibo': 'WeiboCookiesGenerator'
}

# 测试类，如果扩展其他站点，请在此配置
TESTER_MAP = {
    'weibo': 'WeiboValidTester'
}

# 产生器和验证器循环周期
CYCLE = 120

# API地址和端口
API_HOST = '127.0.0.1'
API_PORT = 5000

# 进程开关
# 产生器，模拟登录添加Cookies
GENERATOR_PROCESS = True
# 验证器，循环检测数据库中Cookies是否可用，不可用删除
VALID_PROCESS = False
# API接口服务
API_PROCESS = True