#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-5-28

@author: Allen
'''
from sina.login import SinaLogin
import urllib2
import re
from sina.writer import WeiboDataWriter


class WeiboCrawler(object):
    '''
    classdocs  
    '''
    opener = None
    id = 0
    writer = WeiboDataWriter()
    user = ''
    pwd = ''
    def __init__(self, threadid, user, pwd, proxy):
        '''
        Constructor
        '''
        self.id = threadid
        self.user = user
        self.pwd = pwd
        self.opener = urllib2.build_opener()
        if proxy :
            proxy_support = urllib2.ProxyHandler({'http':'%s' % proxy})  
            self.opener.add_handler(proxy_support)
        self.sina_login = SinaLogin(self.opener)
        if not self.sina_login.login(user, pwd):
            print str(self.id) + ' ' + 'login error!'
            self.opener = None
            
    def extend(self):
        fail_count = 0
        while True:
            uid = self.writer.get_user()
            if uid == None:
                break
            try:
                
                home_url = 'http://weibo.com/u/' + str(uid)
                home_page = self.opener.open(home_url,timeout=10).read()
                uid2 = re.search("\$CONFIG\[\'page_id\'\]\=\'(\d+)\';",home_page).group(1)
                page = 0
                weibo_count = 0
                while page < 10:
                    page += 1
                    ori_url = 'http://weibo.com/p/' + uid2 + '/weibo?is_ori=1&page=' + str(page)
                    weibo_page = self.opener.open(ori_url,timeout=10).read()
                    res = re.findall('feed_list_content[^\>]+\>(.+?)\<\\\\\/div\>',weibo_page)
                    for item in res:
                        item = item[38:]
                        item = re.sub("\<[^\>]+?\>","",item)
                        self.writer.add_data(item)
                        weibo_count += 1
                print str(self.id) + " : " + str(uid) + " " + str(weibo_count)
                fail_count = 0
            except Exception,ex:
                print str(self.id) + " : "
                print Exception,":",ex
                fail_count += 1
                if fail_count >= 10 :
                    print str(self.id) + " : error!"
                    if self.sina_login.login(self.user, self.pwd):
                        print str(self.id) + ' relogin succ'
                        continue
                    else :
                        print str(self.id) + ' relogin fail'
                        print str(self.id) + " : exit!"
                        break
                continue
        


