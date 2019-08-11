#scrapy选择器详解
##1.构造选择器
response对象以```.selector```属性提供了一个selector
```python
response.selector.xpath('//span/text()').extract()
```
##2.使用选择器
```bash
response.xpath()

response.css()
```
##3.嵌套选择器
xpath()和css()返回相同类型的选择器列表，因此你也可以对这些选择调用选择器方法。
##4.结合正则表达式使用选择器
```.re()```方法返回unicode字符串的列表，无法构造嵌套式的```.re()```调用
```.re_first()```提取第一个匹配到的字符串
##5.使用相对xpaths

