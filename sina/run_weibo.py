#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-4-14

@author: Allen
'''
import threading
from sina.weibocrawler import WeiboCrawler

if __name__ == '__main__':
    pass
        
data = [['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ['username', 'password', None],
        ]



def weibo_spider(threadid, user, pwd, proxy):
    t = WeiboCrawler(threadid, user, pwd, proxy)
    if t.opener :
        while t.extend():
            pass

for i in range(len(data)):
    threading.Thread(target=weibo_spider, args=(i, data[i][0], data[i][1], data[i][2])).start()

    