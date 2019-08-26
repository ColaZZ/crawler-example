#Flask+Reids维护动态Cookies池
#Cookies池架构
账号队列--生成器--Cookies队列--定时检测器
#Cookies池的要求
- 自动登陆更新
- 定时验证筛选
- 提供外部接口