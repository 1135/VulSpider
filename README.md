# VulSpider

本程序在后台持续运行，每10分钟爬取一次"最新漏洞"及"每日简报"，如果对比后发现有新内容(最新url链接及其标题），则主动通知给若干安全人员。

### 实现介绍

* 需求背景：爬取若干固定单页面，提取关键信息，实际测试未触发反爬机制。
* 爬虫选型：http获取response + regex正则匹配（无需headless爬虫）
* 网络环境：无需代理
* 定时任务：schedule模块

### 主动通知途径

* 邮箱 通过配置发件箱，发送邮件到若干安全人员的邮箱中。 需要安装:邮件客户端(pc+mobile)
* (undo) ~~slack-bot 需要安装:slack客户端(pc+mobile)~~
* (undo) ~~weixin robot（未实现理由 1.频繁扫QR code授权 2.频繁发送可能被封 3.微信使用范围主要是国内）~~

### 配置参数

发件邮箱地址：将代码中`smtplib.SMTP`中的地址改为发件邮箱地址。
发件邮箱账号：将代码中`_user=`的值改为发件邮箱账号。
发件邮箱密码：将代码中`_pass=`的值改为发件邮箱密码。

收件人邮箱地址列表：将代码中`Recipient_list`的值改为收件人邮箱地址列表。

### Usage
```
#python2
pip install schedule
python VulSpider.py
```

**注意**
* 发件邮箱需要开启SMTP服务(如登录mail.sohu.com "选项" - "设置" 开启 POP3/SMTP服务 和 IMAP/SMTP服务 "保存")
* 建议使用QQ邮箱、sohu邮箱。不建议使用网易邮箱发邮件(实测，发件邮箱发出的部分邮件会被系统退信，收件箱加白的机会都没有)
* 不建议使用腾讯云部署(实测，无法与邮件服务器连接 如smtp.sohu.com等)

### "最新漏洞"——采集地址

* xz.aliyun.com

* exploit-db.com
```
https://www.exploit-db.com/remote/
https://www.exploit-db.com/webapps/
https://www.exploit-db.com/local/
```

* CNVD
```
http://www.cnvd.org.cn/flaw/list.htm
```

* exploitalert.com
```
https://www.exploitalert.com/search-results.html
```

* sec-wiki
```
https://www.sec-wiki.com
```

### "每日简报"——采集地址

* Xuanwulab
```
https://xuanwulab.github.io/cn/secnews/2018/09/03/index.html
```

* cert.360.cn
```
https://cert.360.cn/daily?date=2018-09-03
```
