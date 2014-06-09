#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-4-10

@author: Allen
'''
import time
import urllib2
import urllib
import json
import re
import base64
import rsa
import binascii
import cookielib

class SinaLogin(object):
    '''
    classdocs
    '''

    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_='
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'
    login_header = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
                    }
    ret_rsakv = 0
    ret_servertime = 0
    ret_nonce = ''
    ret_pubkey = ''
    cookiejar = None
    opener = None
    uniqueid = ''
    
    def __init__(self, opener):
        '''
        Constructor
        '''
        self.prelogin_url += str(int(time.time() * 1000))
        self.cookiejar = cookielib.LWPCookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookiejar)
        self.opener = opener
        self.opener.add_handler(cookie_handler)
        ret =self.opener.open(self.prelogin_url).read()
        ret = re.search('{.*}', ret).group()
        data = json.loads(ret)
        self.ret_rsakv = data['rsakv']
        self.ret_servertime = data['servertime']
        self.ret_nonce = data['nonce'] 
        self.ret_pubkey = data['pubkey'] 
        
    def get_pwdcode(self,pwd):
        rsa_e = 0x10001
        pwdcode1 = str(self.ret_servertime) + '\t' + self.ret_nonce + '\n' + str(pwd)
        key = rsa.PublicKey(int(self.ret_pubkey, 16), rsa_e)
        encropy_pwd = rsa.encrypt(pwdcode1.encode('utf_8'), key)
        return binascii.b2a_hex(encropy_pwd)
        
    def login(self, name, pwd): 
        namecode = base64.encodestring(urllib.quote(name))
        pwdcode = self.get_pwdcode(pwd)
        postparam = {
                    'vsnf':         '1',
                    'useticket':    '1',
                    'url':          'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                    'su':           namecode,
                    'sp':           pwdcode,
                    'service':      'miniblog',
                    'servertime':    str(self.ret_servertime),
                    'savestate':    '7',
                    'rsakv':        str(self.ret_rsakv),
                    'returntype':   'META',
                    'pwencode':     'rsa2',
                    'pagerefer':    '',
                    'nonce':        self.ret_nonce,
                    'gateway':      '1',
                    'from':         '',
                    'entry':        'weibo',
                    }
        postdata = urllib.urlencode(postparam)
        req = urllib2.Request(self.login_url)
        req.add_data(postdata)
        for (k,v) in self.login_header.items():
            req.add_header(k, v)
        result = self.opener.open(req)
        text = result.read()
        try:
            url = re.search('location\.replace\(\'(.*)\'\)',text).group(1)
            ret = self.opener.open(url).read()
            self.uniqueid = re.search('\"uniqueid\"\:\"(\d*)\"',ret).group(1)
            return True
        except:
            errorpage = open('d:\\SpiderData\\weibo\\loginerror.html' , 'w')
            errorpage.write(text)
            errorpage.close()
            return False

# opener = urllib2.build_opener()              
# tSinaLogin = SinaLogin(opener)
# tSinaLogin.cookiejar.
# if tSinaLogin.login('', ''):
#     print tSinaLogin.cookiejar.as_lwp_str()
# else :
#     print 'error'