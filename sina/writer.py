#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-4-10

@author: Allen
'''
from threading import Lock


def singleton(cls, *args, **kw):  
    instances = {}  
    def _singleton():  
        if cls not in instances:  
            instances[cls] = cls(*args, **kw)  
        return instances[cls]  
    return _singleton  

@singleton
class UserDataWriter(object):
    '''
    classdocs
    '''
    data_path = 'd:\\SpiderData\\weibo\\user_data.txt'
    users_path = 'd:\\SpiderData\\weibo\\user_info.txt'
    info_path = 'd:\\SpiderData\\weibo\\user_searchinfo.txt'
    data_queue = []
    users = []
    cur_start = 0
    cur_len = 0
    cache_len = 0
    lock = Lock()
    
    def __init__(self):
        '''
        Constructor
        '''
        count = 0
        fp = open(self.data_path, 'r')
        for line in fp:
            linedata = line.strip()
            if linedata.isdigit():
                self.data_queue.append(int(linedata))
            count += 1
        fp.close()
        fp = open(self.info_path, 'r')
        info = fp.readline().split()
        fp.close()
        self.cur_start = int(info[0])
        self.cur_len = int(info[1])
        if count != self.cur_len:
            print str(count) + ' ' + str(self.cur_len)
            self.cur_len = count
#         assert count == self.cur_len
        assert self.cur_start <= self.cur_len
        
    def write_data(self):
        fp = open(self.data_path, 'a')
        for item in self.data_queue[len(self.data_queue) - self.cache_len :]:
            fp.write(str(item) + '\r\n')
        fp.close()
        fp = open(self.users_path, 'a') 
        for item in self.users:
            fp.write(' '.join(item) + '\r\n')
        fp.close()
        self.users = []
        fp = open(self.info_path, 'w')
        fp.write(str(self.cur_start) + ' ' + str(self.cur_len))
        fp.close()
        self.cache_len = 0
        
    def add_user(self, uid, nick, sex, fans_num, follow_num, href, intro):
        with self.lock:
            if not int(uid) in self.data_queue:
                self.users.append([uid, nick, sex, fans_num, follow_num, href, intro])
                self.data_queue.append(int(uid))
                self.cur_len += 1
                self.cache_len += 1
                if self.cache_len >= 200:
                    self.write_data()

    def get_user(self):
        with self.lock:
            if self.cur_start < self.cur_len:
                self.cur_start += 1
                return self.data_queue[self.cur_start]
            return None


@singleton
class WeiboDataWriter(object):
    '''
    classdocs
    '''
    uid_path = 'd:\\SpiderData\\weibo\\user_data.txt'
    info_path = 'd:\\SpiderData\\weibo\\weibo_searchinfo.txt'
    data_path = 'd:\\SpiderData\\weibo\\weibo_data.txt'
    data_queue = []
    users = []
    uid_pos = 0
    lock = Lock()
    
    def __init__(self):
        '''
        Constructor
        '''
        fp = open(self.uid_path, 'r')
        for line in fp:
            linedata = line.strip()
            if linedata.isdigit():
                self.users.append(int(linedata))
        fp.close()
        fp = open(self.info_path,'r')
        self.uid_pos = int(fp.readline().strip())
        fp.close()
        assert self.uid_pos < len(self.users)
        
    def write_info(self):
        fp = open(self.info_path,'w')
        fp.write(str(self.uid_pos))
        fp.close()
    
    def write_data(self):
        fp = open(self.data_path,'a')
        for item in self.data_queue:
            fp.write(item + '\r\n')
        fp.close()
        self.data_queue = []
        
    def get_user(self):
        with self.lock:
            if self.uid_pos < len(self.users):
                ret = self.users[self.uid_pos]
                self.uid_pos += 1
                return ret
            else :
                return None
        
    def add_data(self,data):
        with self.lock:
            self.data_queue.append(data)
            if len(self.data_queue) >= 1000:
                self.write_data()
                self.write_info()
                
    
    
    