#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 定时任务
import schedule
import time

# 正则
import re
# ------
import urllib2
import urllib  # 用于url编码
import cookielib  # cookie管理

import ssl  # 关闭https证书验证

import sys

ssl._create_default_https_context = ssl._create_unverified_context

# gzip
import zlib

# 全局变量---http请求参数配置
headers_dict = {
    'Connection': 'close',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Pragma': 'no-cache',
    'Cache-Control': 'max-age=0',
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.3',
}

data_urlencoded_str = """"""
method = "GET"
debugmode = False
timeout_sec = 60


global_crawl_times = 0

# 全局变量---"内存" 字典（启动时候为空，启动后5分钟对比一次，有新的则加入对应字典）
dict_alert = {}
dict_secwiki = {}
dict_cnvd_global = {}
dict_xz_global = {}
dict_expdb_remote = {}
dict_expdb_local = {}
dict_expdb_webapps = {}


# -------------------------------------

def SENT_resquest(url, headers_dict, timeout_sec, data_urlencoded_str, method, debugmode):

    cookiejar = cookielib.CookieJar()

    if (debugmode == True):
        opener = urllib2.build_opener(
            urllib2.HTTPHandler(debuglevel=1),
            urllib2.HTTPSHandler(debuglevel=1),
        )
    else:
        opener = urllib2.build_opener(
        )


    urllib2.install_opener(opener)

    try:

        if method == 'POST':  # post请求
            req_with_header = urllib2.Request(url)
            req_with_header.data = data_urlencoded_str  # 指定post数据   不写这一行就是get请求

        if method == 'GET':  # get请求
            req_with_header = urllib2.Request(url + data_urlencoded_str)

        # http头信息
        req_with_header.headers = headers_dict  # 参数可以写在圆括号urllib2.Request(url)里   如 (url,headers=headers_dict)

        response_ = urllib2.urlopen(req_with_header, timeout=timeout_sec)  # timeout_sec指定超时时间

        return response_

    except urllib2.HTTPError as e:
        print '----异常信息--------------------'
        print e.geturl()
        print e  # 如果URl 为不存在的地址  会输出HTTP Error 404: Not Found
        print e.code
        print e.reason
        # print e.read()
        # 异常时候也返回 响应包长度
        print '------------------------------'


    else:
        print(response_.read())  # #如果URl 请求成功  会输出 内容 如<!DOCTYP等
        response_.close()

def crawl_alert():
    # ---------------
    # https://www.exploitalert.com/search-results.html
    try:
        url_alert = 'https://www.exploitalert.com/search-results.html'
        resp_alert = SENT_resquest(url_alert, headers_dict, timeout_sec, data_urlencoded_str,
                                   method, debugmode)
        # print resp_alert.headers['content-length']

        response_alert = resp_alert.read().decode("utf8")

        regex_alert = 'href="http.+?">.+?a>'

        regex_obj_url_pre = re.compile(regex_alert)
        result_list_alert = regex_obj_url_pre.findall(response_alert)

        temp_dict = {}  # 本次获取的所有内容
        # print result_list_alert
        for one_url in result_list_alert:
            current_text = one_url[6:].strip('</a>').replace('">', '\t')

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict


    except Exception as e:
        print "error!!!" + str(e)
        return ""

def crawl_expdb(url_expdb):
    try:

        resp_expdb = SENT_resquest(url_expdb, headers_dict, timeout_sec, data_urlencoded_str,
                                   method, debugmode)
        content_encode = resp_expdb.info().get('Content-Encoding')

        resp_text = resp_expdb.read()

        if content_encode == 'gzip':
            resp_text = zlib.decompress(resp_text, zlib.MAX_WBITS | 16)
            print '[*解码gzip]\n'

        elif content_encode == 'deflate':
            resp_text = zlib.decompress(resp_text, -zlib.MAX_WBITS)
            print '[*解码deflate]\n'

        else:
            print '[*无压缩]\n'

        regex_expdb = r"""<a.+data-toggle="tooltip" data-placement="top".+>"""
        regex_obj_url_pre = re.compile(regex_expdb)

        result_list_expdb = regex_obj_url_pre.findall(resp_text)

        temp_dict = {}
        for one_url in result_list_expdb:
            current_text = (
                one_url[9:].strip('">').replace('" data-toggle="tooltip" data-placement="top" title="', "\t"))

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict

    except Exception as e:
        print "error!!!" + str(e)
        print e.message
        return ""


def crawl_xz():

    try:
        url_xz = 'https://xz.aliyun.com'
        resp_xz = SENT_resquest(url_xz, headers_dict, timeout_sec, data_urlencoded_str,
                                method, debugmode)

        response_xz = resp_xz.read().decode("utf8")

        regex_xz = r"""title"  href=".+\n        .+a>"""

        regex_obj_url_pre = re.compile(regex_xz)
        result_list_xz = regex_obj_url_pre.findall(response_xz)

        # print result_list_xz

        temp_dict = {}  # 本次获取的所有内容

        for one_url in result_list_xz:
            current_text = one_url[9:].strip('</a>').replace('\n', '').replace('">', '\t').replace('ref="',url_xz).replace('" target="_blank','').replace("        ", "")
            # print (current_text)
            # print current_text.split('\t')[0]  # url
            # print current_text.split('\t')[1]  # 标题

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict

    except Exception as e:
        print "error!!!" + str(e)
        return ""

def crawl_cnvd():
    # ---------------
    # http://www.cnvd.org.cn

    try:
        url_cnvd = 'http://www.cnvd.org.cn'
        resp_cnvd = SENT_resquest(url_cnvd + "/flaw/list.htm", headers_dict, timeout_sec, data_urlencoded_str,
                                  method, debugmode)

        # print resp_cnvd.headers['content-length']

        response_cnvd = resp_cnvd.read().decode("utf8")

        regex_cnvd = r"""href.+"\s{8,}title=".+">"""
        regex_obj_url_pre = re.compile(regex_cnvd)
        result_list_cnvd = regex_obj_url_pre.findall(response_cnvd)

        #print result_list_cnvd

        temp_dict = {}
        for one_url in result_list_cnvd:
            current_text = url_cnvd + one_url[6:].replace("\n", '').replace("\t", '').replace('"', '').replace(">",
                                                                                                               '').replace(
                'title=', "***")

            # print (current_text)
            # print current_text.split('***')[0]  # url
            # print current_text.split('***')[1]  # 标题
            temp_dict[current_text.split('***')[0]] = current_text.split('***')[1]
        return temp_dict

    except Exception as e:
        print "error!!!" + str(e)
        return ""


def crawl_secwiki():
    try:
        url_secwiki = 'https://www.sec-wiki.com'
        resp = SENT_resquest(url_secwiki, headers_dict, timeout_sec, data_urlencoded_str, method, debugmode)
        response_secwiki = resp.read().decode("utf8")

        regex_secwiki = r"""news' rel='\d{5}'\shref='http[\w:\/\/.].+?</a>"""
        regex_obj_url_pre = re.compile(regex_secwiki)
        result_list = regex_obj_url_pre.findall(response_secwiki)

        #print result_list

        temp_dict = {}
        for one_url in result_list:
            current_text = one_url[24:].strip('</a>').replace("'>", "\t")  # .replace(" ", "")

            # print (current_text)
            #print current_text.split('\t')[0]  # url
            #print current_text.split('\t')[1]  # 标题

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict


    except Exception as e:
        print "error!!!" + str(e)
        return ""


def crawl_all_new():

    crawl_daily_all() #daily

    currentdicts_all_surenew = {}  # 确认为新资讯，则加入该待发送字典dict

    global global_crawl_times
    print "global_crawl_times" + str(global_crawl_times)

    # ---------------secwiki
    print '-' * 20 + 'secwiki new'

    current_dict = crawl_secwiki()  # 返回字典

    global dict_secwiki  # 全局变量

    if current_dict == "":
        print "函数crawl_secwiki返回空字符串"
        pass
    elif global_crawl_times == 1:
        dict_secwiki = current_dict
        print "首次爬取."
    else:
        if dict_secwiki == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_secwiki.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_secwiki = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)

    print '-' * 20 + '\n'

    # ---------------exploitalert.com
    print '-' * 20 + 'exploitalert.com new'

    current_dict = crawl_alert()  # 返回字典

    global dict_alert  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_alert = current_dict.copy()  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_alert == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_alert.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_alert = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)

    print '-' * 20 + '\n'

    # ---------------cnvd

    print '-' * 20 + 'cnvd.org.cn'

    current_dict = crawl_cnvd()  # 本次cnvd抓取结果
    global dict_cnvd_global  # cnvd中的新的

    if current_dict == "":
        print "current is null"
        pass
    elif global_crawl_times == 1:
        dict_cnvd_global = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_cnvd_global == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_cnvd_global.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_cnvd_global = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)


    print '-' * 20 + '\n'
    # ---------------xz.aliyun.com
    print '-' * 20 + 'xz.aliyun.com new'

    current_dict = crawl_xz()  # 本次xz抓取结果
    global dict_xz_global  # xz中的新的

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_xz_global = current_dict.copy()  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_xz_global == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_xz_global.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_xz_global = current_dict
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)

    print '-' * 20 + '\n'

    # ---------------expdb-remote

    print '-' * 20 + 'exploit-db.com/remote/'

    current_dict = crawl_expdb('https://old.exploit-db.com/remote/')  # 本次exploit-db.com/remote抓取结果

    global dict_expdb_remote  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_remote = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_expdb_remote == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_expdb_remote.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_expdb_remote = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)

    print '-' * 20 + '\n'

    # --------------------expdb-webapps

    print '-' * 20 + 'exploit-db.com/webapps/'

    current_dict = crawl_expdb('https://old.exploit-db.com/webapps/')

    global dict_expdb_webapps  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_webapps = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_expdb_webapps == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_expdb_webapps.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_expdb_webapps = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)

    print '-' * 20 + '\n'

    # --------------------expdb-local

    print '-' * 20 + 'exploit-db.com/local/'

    current_dict = crawl_expdb('https://old.exploit-db.com/local/')

    global dict_expdb_local  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_local = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
        print "首次爬取."
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_expdb_local == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_expdb_local.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_expdb_local = current_dict.copy()
                    print str(key)
                    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
                    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)


    print '-' * 20 + '\n'

    # -------------------------------
    print '[爬取次数]global_crawl_times=' + str(global_crawl_times)
    print '-' * 20 + '\n'


    # -------------------------------发邮件
    if global_crawl_times != 1 and currentdicts_all_surenew != {}:
        print '[mail]global_crawl_times=' + str(global_crawl_times)
        print '发送邮件：'
        keyValList = currentdicts_all_surenew.items()  # 获取所有新增的 Key-Value 变量类型:元祖

        alltext = ''
        for k, v in keyValList:  # 遍历
            send_mail_A(Recipient_list, '[*]' + v, v + '\n' + k)
            # 每个漏洞发一条

    #爬行次数+1
    global_crawl_times += 1

    sys.stdout.flush()  # 实时输出日志 适用于 python x.py > x.log的实时输出


def send_mail_163(to_addrs, mail_Subject, mail_content, type='plain'):
    # 登录配置
    _user = '15235756964@163.com'
    _pwd = 'asdqwe1234'  # 网易授权码而不是密码

    # 实测可群发
    # 使用MIMEText构造符合smtp协议的header及body
    msg = MIMEText(mail_content, type, 'utf-8')
    msg["Subject"] = Header(mail_Subject, 'utf-8')
    msg["From"] = Header(_user, 'utf-8')  # 发件人
    msg["To"] = ",".join(to_addrs)  # Header(",".join(to_addrs), 'utf-8')

    # -----打印时间
    current_now = datetime.datetime.now()
    print str(current_now)

    try:
        s = smtplib.SMTP("smtp.163.com", timeout=30)  # 连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)  # 登陆服务器
        s.sendmail(_user, to_addrs, msg.as_string())  # 发送邮件

    except Exception as e:
        global mail_error_times
        mail_error_times += 1

        print "[发邮件异常]mail error!!!" + str(e)
        print "[发邮件异常]第%s次" % str(mail_error_times)
        if mail_error_times < 10:
            send_mail_163(to_addrs, mail_Subject, mail_content, type='plain')
        else:
            print "[发邮件异常]10次"
            current_now = datetime.datetime.now()
            print str(current_now)
            pass

# qq邮箱
def send_mail_A(to_addrs, mail_Subject, mail_content, type='plain'):
    _user = 'user@qq.com'
    _pwd = 'pass'

    # 使用MIMEText构造符合smtp协议的header及body
    msg = MIMEText(mail_content, type, 'utf-8')
    msg["Subject"] = Header(mail_Subject, 'utf-8')
    msg["From"] = Header("VulPush <" + _user + ">", )  # 'utf-8')  # 发件人
    msg["To"] = ",".join(to_addrs)  # Header(",".join(to_addrs), 'utf-8')

    try:
        s = smtplib.SMTP("smtp.qq.com", timeout=30)  # 连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)  # 登陆服务器
        s.sendmail(_user, to_addrs, msg.as_string())  # 发送邮件
    except Exception as e:
        global mail_error_times
        mail_error_times += 1
        print "[发邮件异常]fail - send_mail_A " + str(e)
        print "[发邮件异常]第%s次" % str(mail_error_times)
        if mail_error_times < 100:  # 调用另一个发邮件函数
            current_now = datetime.datetime.now()
            print str(current_now)
            # 二者互相调用  此处调用send_mail_B
            print "[发邮件]换发件箱 - send_mail_B"
            send_mail_B(to_addrs, mail_Subject, mail_content, type='plain')
        else:
            print "[发邮件异常]发件箱A 发件箱B 共失败超过100次!!! 可能是网络问题" + str(e)
            print "失败次数清零 持续运行"
            mail_error_times = 0

#sohu
def send_mail_B(to_addrs, mail_Subject, mail_content, type='plain'):
    _user = 'user@sohu.com'
    _pwd = 'pass.'

    # 使用MIMEText构造符合smtp协议的header及body
    msg = MIMEText(mail_content, type, 'utf-8')
    msg["Subject"] = Header(mail_Subject, 'utf-8')
    msg["From"] = Header("VulPush <" + _user + ">", )  # 'utf-8')  # 发件人
    msg["To"] = ",".join(to_addrs)  # Header(",".join(to_addrs), 'utf-8')

    try:
        s = smtplib.SMTP("smtp.sohu.com", timeout=30)  # 连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)  # 登陆服务器
        s.sendmail(_user, to_addrs, msg.as_string())  # 发送邮件
    except Exception as e:
        # 如果异常 重发达10次仍异常则退出程序
        global mail_error_times
        mail_error_times += 1
        print "[发邮件异常]fail - send_mail_A " + str(e)
        print "[发邮件异常]第%s次" % str(mail_error_times)

        if mail_error_times < 100:  # 调用另一个发邮件函数
            # 打印当前时间
            current_now = datetime.datetime.now()
            print str(current_now)
            # 二者互相调用  此处调用send_mail_A
            print "[发邮件]换发件箱 - send_mail_A"
            send_mail_A(to_addrs, mail_Subject, mail_content, type='plain')
        else:
            print "[发邮件异常]发件箱A 发件箱B 共失败超过100次!!! 可能是网络问题" + str(e)
            print "失败次数清零 持续运行"
            mail_error_times = 0


# 爬daily----------------------------------V
# 全局变量
import datetime

start_time = datetime.datetime.now()  # 程序启动时的时间

# 今天发过了吗
today_has_send_360cert = 0
today_has_send_xuanwulab = 0

# 发邮件失败次数
mail_error_times = 0


def crawl_360cert(riqi):
    # https://cert.360.cn/daily?date=
    try:
        print "crawl_360cert riqi" + str(riqi)
        url_today = 'https://cert.360.cn/daily?date=' + str(riqi)
        print "current url" + url_today

        resp_today = SENT_resquest(url_today, headers_dict, timeout_sec, data_urlencoded_str,
                                  method, debugmode)


        content_encode = resp_today.info().get('Content-Encoding')
        resp_text = resp_today.read()

        if content_encode == 'gzip':
            resp_text = zlib.decompress(resp_text, zlib.MAX_WBITS | 16)
            print '[*解码gzip]\n'
        elif content_encode == 'deflate':
            resp_text = zlib.decompress(resp_text, -zlib.MAX_WBITS)
            print '[*解码deflate]\n'
        else:
            print '[*无压缩]\n'

        print "Response:\n"
        print resp_text  # 打印response的html内容

        print "360cert len response:" + str(len(resp_text))
        if len(resp_text) < 2800:#通常2712
            return "0"  # 单日信息还未出来
        if ('Information' not in resp_text) and ('Vulnerability' not in resp_text):
            return "0"

        # 直接匹配
        regex = r"""(report-title">.+\n.+" t)|(<div class="block-title">.+</span>)"""
        matches = re.finditer(regex, resp_text)

        alltext = ""
        for matchNum, match in enumerate(matches):
            #matchNum = matchNum + 1

            item = match.group()[14:].replace('ock-title">', "------- ").replace('</span>', ' -------\n\n').replace(
                '<span class="english">', '').replace('<div class="report-link"><a href="', '').replace('" t',
                                                                                                        "\n\n").replace(
                '</div>', "").replace("                        ", "")

            print item
            alltext += item

        # 增加url
        alltext = url_today + "\n\n" + alltext

        return alltext

    except Exception as e:
        print "error!!!" + str(e)
        return "error"


def crawl_xuanwu(riqi):
    # https://xuanwulab.github.io/cn/secnews/2018/09/03/index.html
    try:
        print "crawl_xuanwulab riqi" + str(riqi)
        nian = ""
        yue = ""
        ri = ""

        nian = riqi.split('-')[0]
        if len(riqi.split('-')[1]) == 1:
            yue = "0" + riqi.split('-')[1]
        else:
            yue =riqi.split('-')[1]
        if len(riqi.split('-')[2]) == 1:
            ri = "0" + riqi.split('-')[2]
        else:
            ri = riqi.split('-')[2]

        url_xuanwutoday = 'https://xuanwulab.github.io/cn/secnews/{}/{}/{}/index.html'.format(nian, yue, ri)
        print "current url_xuanwutoday:" + url_xuanwutoday

        resp_xw = SENT_resquest(url_xuanwutoday, headers_dict, timeout_sec, data_urlencoded_str,
                                method, debugmode)

        if resp_xw:
            content_encode = resp_xw.info().get('Content-Encoding')
            if content_encode == 'gzip':
                response_xw = zlib.decompress(resp_xw, zlib.MAX_WBITS | 16)
                print '[*解码gzip]\n'

            elif content_encode == 'deflate':
                response_xw = zlib.decompress(resp_xw, -zlib.MAX_WBITS)
                print '[*解码deflate]\n'

            else:
                print '[*无压缩]\n'
                response_xw = resp_xw.read()  # .decode("utf8")
            print response_xw  # 打印response的内容
        else:
            return "0"  # 单日信息还未出来

        print "Xuanwulab len response:" + str(len(response_xw))

        if ('Xuanwu' not in response_xw):
            return "0"

        # 直接匹配
        regex = r"""<span class="category">.+rel"""

        matches = re.finditer(regex, response_xw, re.MULTILINE)

        alltext = ""
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1

            item = "{matchNum} {match}".format(matchNum=matchNum,
                                               match=match.group()[23:].replace("</span>  ", "").replace("<a href=\"",
                                                                                                         '\n').replace(
                                                   "\" rel", '').replace("\"nofollow\">", "").replace("</a>", "\n"))

            print item

            alltext += (item + "\n\n")

        alltext = url_xuanwutoday + "\n\n" + alltext
        return alltext

    except Exception as e:
        print "error!!!" + str(e)
        return "error"


def crawl_daily_all():  # 360cert + xuanwulab
    global today_has_send_360cert
    global today_has_send_xuanwulab

    current_now = datetime.datetime.now()
    current_riqi = str(current_now.year) + '-' + str(current_now.month) + '-' + str(current_now.day)
    print "current_now:" + str(current_now)
    print "current_riqi:" + current_riqi

    if str(current_now.hour) == "0" or str(current_now.hour) == "1":  # 凌晨了 今日发送 改为 0
        today_has_send_360cert = 0
        today_has_send_xuanwulab = 0


    if today_has_send_360cert == 0:  # 没发过
        temp360resp = crawl_360cert(current_riqi)
        if temp360resp == "0":  # 360cert请求失败 或 当日的每日播报还没出来
            print "[360cert]当日暂未出新内容"
            print str(current_now)
            pass  # 不更改flag时间
        elif temp360resp == "error":
            print "[360cert]请求异常"
            print str(current_now)
        else:
            print str(current_now)
            print "[360cert] will send"
            send_mail_A(Recipient_list, '[*]360cert ' + current_riqi, temp360resp, type='plain')
            today_has_send_360cert = 1
    else:
        print "[360cert] 今天已发过了"

    if today_has_send_xuanwulab == 0:  # 没发过
        tempxuanwu = crawl_xuanwu(current_riqi)
        if tempxuanwu == "0":  # 360cert请求失败 或 当日的每日播报还没出来
            print "[xuanwulab]当日暂未出新内容"
            print str(current_now)
            pass  # 不更改flag时间
        elif tempxuanwu == "error":
            print "[xuanwulab]请求异常"
            print str(current_now)
        else:
            print str(current_now)

            print "[xuanwulab] will send"
            # send_mail_163_to_all('[*]360cert daily',,temp360resp, type='plain')
            send_mail_A(Recipient_list, '[*]xuanwulab ' + current_riqi, tempxuanwu, type='plain')
            today_has_send_xuanwulab = 1

    else:
        print "[xuanwulab] 今天已发过了"

    sys.stdout.flush()  # 实时输出日志 适用于 python x.py > x.log的实时输出

# 爬daily----------------------------------^️
# 全局变量
schedule.every(8).minutes.do(crawl_all_new)  # 方法名后面不带括号，就可以执行成功。

# 收件人
Recipient_list = ['1111@126.com','2222@163.com']

if __name__ == '__main__':
    print 'start_time程序启动时间:' + str(start_time)

    global_crawl_times += 1  # 已经爬行次数
    crawl_all_new()
    sys.stdout.flush()

    while True:
        schedule.run_pending()
        time.sleep(30)
        print("alive..")
        sys.stdout.flush()
