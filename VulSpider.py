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
}  # 定制 resquest HTTP头

data_urlencoded_str = """"""  # 作为post参数
print data_urlencoded_str
method = "GET"  # 只支持 POST 或 GET
debugmode = False  # 为True 则输出调试: http请求响应具体内容
timeout_sec = 60  # 请求超时时间 秒

# crawl_all()函数执行的次数
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
    # install_cookie_handler------------------
    cookiejar = cookielib.CookieJar()

    if (debugmode == True):
        # install_debug_handler
        opener = urllib2.build_opener(
            urllib2.HTTPHandler(debuglevel=1),  # 调试：打印输出 HTTP和HTTPS 发包收包信息
            urllib2.HTTPSHandler(debuglevel=1),

            # urllib2.HTTPCookieProcessor(cookiejar),  # 使用CookieJar 自动cookie管理  进行初始化
            # urllib2.HTTPSCookieProcessor(cookiejar), #HTTpS

            # urllib2.ProxyHandler({'http': '127.0.0.1:8080', 'https': '127.0.0.1:8080'}),  # 开启代理！

        )
    else:
        opener = urllib2.build_opener(
            # urllib2.HTTPCookieProcessor(cookiejar),
            # urllib2.ProxyHandler({'http': '127.0.0.1:8080', 'https': '127.0.0.1:8080'}),  # 开启代理！

        )

    # 在这里指定http头 则每个请求都会自动带上   比如User-agent
    # opener.addheaders = [('User-agent', 'Mozilla/5.0  Gecko/20100101 Firefox/44.0')]

    urllib2.install_opener(opener)  # 将某些opener设置为系统默认。只能用一次。如果第二次传入opener，就使用第二次传入的opener。而不能新增opener

    # 发起请求----------------------
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
        print '--------------------------------'


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
            # print (current_text)
            # print current_text.split('\t')[0]  # url
            # print current_text.split('\t')[1]  # 标题

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict
        # #如果 dict_alert 没有该新k-v 则在temp里增加该新k-v （同时更新dict_alert供下次比较）
        # if dict_alert.has_key(current_text.split('\t')[0]) == False:
        #     dict_alert[current_text.split('\t')[0]] = current_text.split('\t')[1]
        # else:
        #     temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        #     dict_alert[current_text.split('\t')[0]] = current_text.split('\t')[1]


    except Exception as e:
        print "error!!!" + str(e)
        return ""
        

def crawl_expdb(url_expdb):
    # ---------------
    # https://www.exploit-db.com/remote/
    # <a.+data-toggle="tooltip" data-placement="top".+>

    try:

        resp_expdb = SENT_resquest(url_expdb, headers_dict, timeout_sec, data_urlencoded_str,
                                   method, debugmode)

        # print resp_expdb.headers['content-length']


        content_encode = resp_expdb.info().get('Content-Encoding')

        resp_text = resp_expdb.read()
        # print '原始：'+ resp_text #可能为gzip压缩的 也可能直接明文

        if content_encode == 'gzip':
            resp_text = zlib.decompress(resp_text, zlib.MAX_WBITS | 16)
            print '[*解码gzip]\n'

        elif content_encode == 'deflate':
            resp_text = zlib.decompress(resp_text, -zlib.MAX_WBITS)
            print '[*解码deflate]\n'

        else:
            print '[*无压缩]\n'

            # print resp_text  # 正确Body

        regex_expdb = r"""<a.+data-toggle="tooltip" data-placement="top".+>"""
        regex_obj_url_pre = re.compile(regex_expdb)

        result_list_expdb = regex_obj_url_pre.findall(resp_text)

        # print result_list_expdb

        # print result_list_expdb
        temp_dict = {}  # 本次获取的所有内容
        for one_url in result_list_expdb:
            current_text = (
                one_url[9:].strip('">').replace('" data-toggle="tooltip" data-placement="top" title="', "\t"))

            # print (current_text)
            # print current_text.split('\t')[0]  # url
            # print current_text.split('\t')[1]  # 标题
            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        print '[*' + str(temp_dict)
        return temp_dict

    except Exception as e:
        print "error!!!" + str(e)
        return ""

def crawl_xz():
    # ---------------
    # https://xz.aliyun.com/

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
            current_text = one_url[9:].strip('</a>').replace('\n', '').replace(
                "       ", "").replace('">', '\t').replace('ref="',url_xz).replace('" target="_blank','')
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

        print result_list_cnvd

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

        # print resp.headers['content-length']

        # 返回/打印 response 内容
        response_secwiki = resp.read().decode("utf8")
        # print response_secwiki


        regex_secwiki = r"""news' rel='\d{5}'\shref='http[\w:\/\/.].+?</a>"""
        # regex_secwiki = r"""\d+' href='[\w:\/\/.-]+'>.+<\/a>"""
        regex_obj_url_pre = re.compile(regex_secwiki)  # 正则表达式里的 . 本来无法匹配换行 加上这个时,  就可以匹配所有字符【包括换行 tab等！！】
        result_list = regex_obj_url_pre.findall(response_secwiki)

        print result_list

        temp_dict = {}
        for one_url in result_list:
            current_text = one_url[24:].strip('</a>').replace("'>", "\t")  # .replace(" ", "")

            # print (current_text)
            print current_text.split('\t')[0]  # url
            print current_text.split('\t')[1]  # 标题

            temp_dict[current_text.split('\t')[0]] = current_text.split('\t')[1]
        return temp_dict


    except Exception as e:
        print "error!!!" + str(e)
        return ""


def crawl_all_new():

    currentdicts_all_surenew = {}  # 确认为新资讯，则加入该待发送字典dict

    global global_crawl_times
    print "global_crawl_times" + str(global_crawl_times)

    # ---------------secwiki
    print '-' * 20 + 'secwiki new'

    current_dict = crawl_secwiki()  # 返回字典

    global dict_secwiki  # 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_secwiki = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
    else:  # 第二次及以后爬取时 进行判断逻辑
        if dict_secwiki == current_dict:  # 前后2次爬取 内容无变化则不操作 tempdict_surenew_alert仍为空
            pass
        else:  # 前后2次爬取 内容有变化
            for key in current_dict.keys():  # 获取本次获得的所有Key
                if dict_secwiki.has_key(key):
                    pass
                else:  # 如果 全局字典dict_alert 不含有 本次获得的某个Key 则为新key
                    currentdicts_all_surenew[key] = current_dict[key]  # 确认为新key
                    dict_secwiki = current_dict.copy()

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局dict_secwiki字典长度：" + str(len(dict_secwiki))
    print "全局dict_secwiki字典内容：" + str(dict_secwiki)

    # ---------------exploitalert.com
    print '-' * 20 + 'exploitalert.com new'

    current_dict = crawl_alert()  # 返回字典

    global dict_alert  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_alert = current_dict.copy()  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局dict_alert字典长度：" + str(len(dict_alert))
    print "全局dict_alert字典内容：" + str(dict_alert)

    # ---------------cnvd

    print '-' * 20 + 'cnvd.org.cn'

    current_dict = crawl_cnvd()  # 本次cnvd抓取结果
    global dict_cnvd_global  # cnvd中的新的

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_cnvd_global = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局cnvd字典长度：" + str(len(dict_cnvd_global))
    print "全局cnvd字典内容：" + str(dict_cnvd_global)

    # ---------------xz.aliyun.com
    print '-' * 20 + 'xz.aliyun.com new'

    current_dict = crawl_xz()  # 本次xz抓取结果
    global dict_xz_global  # xz中的新的

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_xz_global = current_dict.copy()  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局xz字典长度：" + str(len(dict_xz_global))
    print "全局xz字典内容：" + str(dict_xz_global)

    # ---------------expdb-remote

    print '-' * 20 + 'exploit-db.com/remote/'

    current_dict = crawl_expdb('https://www.exploit-db.com/remote/')  # 本次exploit-db.com/remote抓取结果

    global dict_expdb_remote  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_remote = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局ed-remote字典长度：" + str(len(dict_expdb_remote))
    print "全局ed-remote字典内容：" + str(dict_expdb_remote)

    # --------------------expdb-webapps

    print '-' * 20 + 'exploit-db.com/webapps/'

    current_dict = crawl_expdb('https://www.exploit-db.com/webapps/')

    global dict_expdb_webapps  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_webapps = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局ed_webapps字典长度：" + str(len(dict_expdb_webapps))
    print "全局ed_webapps字典内容：" + str(dict_expdb_webapps)

    # --------------------expdb-local

    print '-' * 20 + 'exploit-db.com/local/'

    current_dict = crawl_expdb('https://www.exploit-db.com/local/')

    global dict_expdb_local  # exploit-db.com/remote中的新的 全局变量

    if current_dict == "":
        pass
    elif global_crawl_times == 1:
        dict_expdb_local = current_dict  # 初次爬取 将alert中获取的内容 赋值给 全局字典dict_alert
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

    print "currentdicts_all_surenew字典长度：" + str(len(currentdicts_all_surenew))
    print "currentdicts_all_surenew字典内容：" + str(currentdicts_all_surenew)
    print "全局ed_local字典长度：" + str(len(dict_expdb_local))
    print "全局ed_local字典内容：" + str(dict_expdb_local)

    # crawl_expdb('https://www.exploit-db.com/local/')


    # -------------------------------发邮件
    if global_crawl_times != 1 and currentdicts_all_surenew != {}:
        print '[mail]global_crawl_times=' + str(global_crawl_times)

        print '发送邮件：'
        keyValList = currentdicts_all_surenew.items()  # 获取所有新增的 Key-Value 变量类型:元祖

        alltext = ''
        for k, v in keyValList:  # 遍历
            # alltext += "%s\n%s\n\n" % (v, k)
            send_mail_sohu(Recipient_list, '[*]' + v, v + '\n' + k)


    global_crawl_times += 1

def send_mail_sohu(to_addrs, mail_Subject, mail_content, type='plain'):
    _user = 'sender@sohu.com'#邮箱账号
    _pwd = 'pass'  #邮箱密码

    # 实测可群发

    # 使用MIMEText构造符合smtp协议的header及body
    msg = MIMEText(mail_content, type, 'utf-8')
    msg["Subject"] = Header(mail_Subject, 'utf-8')
    msg["From"] = Header("VulPush <" + _user + ">",)  # 设置发件人名称为VulPush
    msg["To"] = ",".join(to_addrs)  # Header(",".join(to_addrs), 'utf-8')

    try:
        s = smtplib.SMTP("smtp.sohu.com", timeout=30)  # 连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)  # 登陆服务器
        s.sendmail(_user, to_addrs, msg.as_string())  # 发送邮件
    except Exception as e:
        # 如果异常 重发达10次仍异常则退出程序
        global mail_error_times
        mail_error_times += 1
        print "[发邮件异常]mail error!!!" + str(e)
        print "[发邮件异常]第%s次" % str(mail_error_times)
        if mail_error_times < 10:  # 递归调用
            send_mail_sohu(to_addrs, mail_Subject, mail_content, type='plain')
        else:
            print "[发邮件异常]10次重连失败，程序退出!!!" + str(e)
            exit(0)

            # finally:
            #     s.close()



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
        url_cnvd = 'https://cert.360.cn/daily?date=' + str(riqi)
        print "current url" + url_cnvd
        resp_cnvd = SENT_resquest(url_cnvd, headers_dict, timeout_sec, data_urlencoded_str,
                                  method, debugmode)

        response_cnvd = resp_cnvd.read().decode("utf8")

        print "360cert len response:" + str(len(response_cnvd))
        if len(response_cnvd) == 2712:
            return "0"  # 单日信息还未出来
        if ('Report' not in response_cnvd) and ('Security' not in response_cnvd):
            return "0"

        # 过滤掉js 即可避免进入垃圾箱

        # 直接匹配
        regex = r"""(report-title">.+\n.+" t)|(<div class="block-title">.+</span>)"""
        matches = re.finditer(regex, response_cnvd)

        alltext = ""
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1

            item = match.group()[14:].replace('ock-title">', "------- ").replace('</span>', ' -------\n\n').replace(
                '<span class="english">', '').replace('<div class="report-link"><a href="', '').replace('" t',
                                                                                                        "\n\n").replace(
                '</div>', "").replace(" ", "")

            print item
            alltext += item

            # for groupNum in range(0, len(match.groups())):
            #     groupNum = groupNum + 1

        return alltext

    except Exception as e:
        print "error!!!" + str(e)
        return "error"


def crawl_xuanwu(riqi):
    # https://xuanwulab.github.io/cn/secnews/2018/09/03/index.html
    # 个位数 必须加零 如09 03
    try:
        print "crawl_xuanwulab riqi" + str(riqi)
        nian = ""
        yue = ""
        ri = ""

        nian = riqi.split('-')[0]
        if len(riqi.split('-')[1]) == 1:
            yue = "0" + riqi.split('-')[1]
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

        # 过滤掉js 即可避免进入垃圾箱

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

            # for groupNum in range(0, len(match.groups())):
            #     groupNum = groupNum + 1

        return alltext

    except Exception as e:
        print "error!!!" + str(e)
        return "error"


def crawl_daily_all():  # 一小时执行一次
    # if daily_xuanwu != 0:
    #     crawl_xuanwu()
    #     global daily_xuanwu
    #     daily_xuanwu = 1
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
            send_mail_sohu(Recipient_list, '[*]360cert ' + current_riqi, temp360resp, type='plain')

            # 更改发送状态
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
            send_mail_sohu(Recipient_list, '[*]xuanwulab ' + current_riqi, tempxuanwu, type='plain')

            # 更改发送状态
            today_has_send_xuanwulab = 1

    else:
        print "[xuanwulab] 今天已发过了"


# 爬daily----------------------------------^️

# 全局变量
schedule.every(10).minutes.do(crawl_all_new)  # 方法名后面不带括号，就可以执行成功。
schedule.every(1).hour.do(crawl_daily_all)  # 方法名后面不带括号，就可以执行成功。

# 收件人
Recipient_list = ['123456@qq.com', 'aaaaa@163.com']

if __name__ == '__main__':
    print 'start_time程序启动时间:' + str(start_time)

    global_crawl_times += 1  # 已经爬行次数
    # print '[start]-> global_crawl_times=' + str(global_crawl_times)
    crawl_daily_all()
    crawl_all_new()

    while True:
        schedule.run_pending()
        time.sleep(30)
        print("alive..")


'''
https://www.sec-wiki.com

https://www.exploit-db.com/
https://www.exploit-db.com/remote/
https://www.exploit-db.com/webapps/
https://www.exploit-db.com/local/

http://www.cnvd.org.cn/flaw/list.htm
https://www.exploitalert.com/search-results.html

'''
