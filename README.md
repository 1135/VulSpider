# VulSpider

本程序在后台持续运行，获取"最新漏洞"及"每日简报"，发送邮件给安全人员。

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
* 不建议使用网易邮箱发邮件(实测，发件邮箱发出的部分邮件会被系统退信，收件箱加白的机会都没有)
* 不建议使用腾讯云部署(实测，无法与邮件服务器连接 如smtp.sohu.com等)

### "最新漏洞"——采集地址

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

