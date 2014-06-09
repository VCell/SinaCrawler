#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-4-14

@author: Allen
'''
import threading
from sina.usercrawler import UserCrawler

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

def user_spider(threadid, user, pwd, proxy):
    t = UserCrawler(threadid, user, pwd, proxy)
    if t.opener :
        while t.extend():
            pass
        

for i in range(len(data)):
    threading.Thread(target=user_spider, args=(i, data[i][0], data[i][1], data[i][2])).start()



    