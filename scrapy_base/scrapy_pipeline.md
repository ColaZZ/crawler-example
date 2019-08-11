# Scrapy中Pipeline的用法
## 1.item pipeline的一些典型应用：
- 清理HTML数据
- 验证爬取的数据（检查item包含某些字段）
- 查重（并丢弃）
- 将爬取结果保存到数据库中
## 2.编写你自己的item pipeline
每个item pipeline组件是一个独立的python类，同时必须实现以下方法：
###2.1 process_item(self, item, spider)
每个item pipeline组件都需要调用该方法返回一个具有数据的dict，或是Item
（或任何继承类）对象，或是抛出DropItem异常，被丢弃的item将不会被之后的pipeline
组件所处理。
- item：被爬取的item
- spider：爬取该item的spider
###2.2 open_spider(self, spider)
spider被开启时，这个方法被调用
- spider：被开启的spider
###2.3 close_spider(self, spider)
spider被关闭时，这个放大被调用
- spider：被关闭的spider