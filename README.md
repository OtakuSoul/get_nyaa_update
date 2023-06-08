# get nyaa update
***
这是一个用于监控nyaa中里番更新的工具，每次都需要去网站上查看是否更新，因此想爬取网站数据自动通知是否更新

## 安装依赖
```
pip install -r requirements.txt
```
## 功能
默认每30分钟去代码中url的网页获取是否有更新

更新的标准是比`stored_data.json`里存储的更新的数据或最新到上个月为止的数据(由于只用于更新提醒，所以没有跨页查询)，然后把最新的一条数据写入`stored_data.json`

对于默认地址使用文件名中[YYMMDD]的发布日期比较，否则使用上传日期比较

如果检查到更新，右下角有弹窗提醒,通过点击可用默认浏览器打开

![](nyaa_get_update.png)

如果网络和代理问题导致网页无法网页，右下角会有警告的弹窗，但是没有点击回调

会将运行时的日志写入logs文件夹下

## 注意
`stored_data.json`可以没有或者为空，但是不能没有timestamp字段

请保证电脑可以访问url中的网页

弹窗使用的是win10toast,其它系统可以使用代码中的plyer进行通知，但是没有点击回调功能