#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-4-10

@author: Allen
'''
from sina.login import SinaLogin
import urllib2
import re
from bs4 import BeautifulSoup
import json
from sina.writer import UserDataWriter
import traceback

class UserCrawler(object):
    '''
    classdocs
    '''
    user = ''
    pwd = ''
    sina_login = None
    writer = UserDataWriter()
    extend_list = []
    done_list = []
    user_table = []
    opener = None
    id = 0
    error_count = 0

    def __init__(self, threadid, user, pwd, proxy):
        '''
        Constructor
        '''
        self.id = threadid
        self.opener = urllib2.build_opener()
        if proxy :
#        设置代理会引起登录验证码。有可能是异地登录的原因。如果能找到本地的代理可以试试
            proxy_support = urllib2.ProxyHandler({'http':'%s' % proxy})  
            self.opener.add_handler(proxy_support)
        self.sina_login = SinaLogin(self.opener)
        if not self.sina_login.login(user, pwd):
            print str(self.id) + ' ' + 'login error!'
            self.opener = None
       
    def get_baselist(self):
        myuid = self.sina_login.uniqueid
        url = 'http://weibo.com/' + myuid + '/myfollow'
        html = self.opener.open(url, timeout=10).read()
        follow_start = '<script>STK && STK.pageletM && STK.pageletM.view('
        follow_end = ')</script>'
        base_count = re.search('全部关注\((\d*)\)', html).group(1)
        base_count = int(base_count)
        for page in range(0, (base_count + 1) / 30 + 1):
            if page != 0:  
                url = url + '?t=1&page=' + str(page + 1)
                html = self.opener.open(url, timeout=10).read()
            for line in html.splitlines():
                if line.startswith(follow_start + '{"pid":"pl_relation_myfollow"'):
                    followjson = json.loads(line[len(follow_start):-len(follow_end)])
                    followsoup = BeautifulSoup(followjson['html'])
                    follows = followsoup.findAll('div', 'myfollow_list S_line2 SW_fun')
                    for follow in follows:
                        info_str = follow.findAll('a', 'S_link2')[0]['action-data']
                        uid = re.search('\&uid\=(\d*)\&', info_str).group(1)
                        nick = re.search('\&nick\=([^&]*)\&', info_str).group(1)
                        sex = re.search('\&sex\=([fm]*)$', info_str).group(1)
                        href = follow.findAll('a', 'S_func1')[0]['href']
                        intro = follow.findAll('div', 'S_txt2')[0].string.strip()
                        
                        self.writer.add_user(uid, nick, sex, '-', '-', href, intro)
                    break
        self.writer.write_data()
        return
        
    def analysis_html(self, url, num_re):
        html = ''
        count = 0
        try:
#             print str(self.id) + ' ' + url
            html = self.opener.open(url, timeout=10).read()
            script_start = '<script>FM.view('
            script_end = ')</script>'
            script_tag = '{"ns":"pl.content.followTab.index"'
            num = 1
            page = 1
# 只爬前10页，之后的由于防爬规则是爬不到的
            while page <= (num - 1) / 20 + 1 and page <= 10:
                if page != 1:
                    try :
#                         print str(self.id) + ' ' + url + str(page)
                        html = self.opener.open(url + str(page), timeout=10).read()
                    except Exception , e:
                        print str(self.id) + ' page down error' 
                        print e
                        page += 1
                        continue
                for line in html.splitlines():
                    if line.startswith(script_start + script_tag):
                        if page == 1:
                            num = int(re.search(num_re, html).group(1))
                        followjson = json.loads(line[len(script_start):-len(script_end)])
                        followsoup = BeautifulSoup(followjson['html'])
                        follows = followsoup.findAll('li', 'clearfix S_line1')
                        for follow in follows:
                            info_str = follow['action-data']
                            f_uid = re.search('^uid\=(\d*)\&', info_str).group(1)
                            nick = re.search('\&fnick\=([^&]*)\&', info_str).group(1)
                            sex = re.search('\&sex\=([fm]*)$', info_str).group(1) 
                            href = follow.findAll('a', target='_blank')[0]['href']
                            if follow.findAll('div', 'info'):
                                intro = follow.findAll('div', 'info')[0].string.strip().replace('\n', ' ')
                            else:
                                intro = '他还没有填写个人简介'
                            fans_num = follow.findAll('a', href='/' + f_uid + '/fans')[0].string
                            follow_num = follow.findAll('a', href='/' + f_uid + '/follow')[0].string
# 一些广告微博会对语料有影响，用这个规则过滤
                            if not (int(follow_num) > 1000 and int(follow_num) > 4 * int(fans_num)):
                                self.writer.add_user(f_uid, nick, sex , fans_num, follow_num, href, intro)
                                count += 1
                        break  
                page += 1
        except Exception , e:
            errorpage = open('d:\\SpiderData\\weibo\\errorpage.html' , 'w')
            errorpage.write(html)
            errorpage.close()
            print str(self.id) + ' ' + 'get page error:'
            print traceback.print_exc()
            print e
            self.writer.write_data()
        return count
                    
    def extend(self):
        uid = self.writer.get_user()
        if uid != None:
            print str(self.id) + ' ' + 'extend ' + str(uid)
            follow_url = 'http://weibo.com/' + str(uid) + '/follow?page='
            fans_url = 'http://weibo.com/' + str(uid) + '/follow?relate=fans&page='
# follow:
            follow_num = self.analysis_html(follow_url, '关注了(\d*)人')
# fans
            fans_num = self.analysis_html(fans_url, '已有(\d*)人关注了')
            print str(self.id) + ' follow:' + str(follow_num) + ' fans:' + str(fans_num)
            if follow_num + fans_num == 0:
                self.error_count += 1
                print str(self.id) + ' extend none'
                if self.error_count >= 100:
                    print str(self.id) + fans_url
                    if self.sina_login.login(self.user, self.pwd):
                        print str(self.id) + ' relogin succ'
                        return True
                    else :
                        print str(self.id) + ' relogin fail'
                        return False
            return True
        else :
            return False
        


