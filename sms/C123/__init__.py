#!/usr/bin/env python
# encoding: utf-8

import requests
from xml.etree import ElementTree as ET

url = {'send': 'http://smsapi.c123.cn/OpenPlatform/OpenApi',
       'data': 'http://smsapi.c123.cn/DataPlatform/DataApi'}

params = {'ac': '1001@500920850001',
          'authkey': '2423E1649E2222DDC82B7027BBE1A7D1',
          'cgid': '52'}

class C123:
    ac = None
    authkey = None
    cgid = None
    csid = None
    response = None

    def __init__(self):
        pass

    def setup(self, ac, authkey, cgid, csid):
        self.ac = ac
        self.authkey = authkey
        self.cgid = cgid
        self.csid = csid

    def params_send(self, text, numbers, t=None, **kwargs):
        if isinstance(numbers, list) == False:
            numbers = [numbers]

        require = {'ac': self.ac,
                   'authkey': self.authkey,
                   'cgid': self.cgid,
                   'csid': self.csid,
                   'c': self.params_text(text),
                   'm': ','.join([str(num) for num in numbers])}
        ret = dict(require, **kwargs)
        if t is not None:
            ret['t'] = t
        return ret
    
    def params_auth(self, **kwargs):
        require = {'ac': self.ac,
                   'authkey': self.authkey}
        ret = dict(require, **kwargs)
        return ret

    def params_text(self, text):
        if isinstance(text, list):
            return '|'.join(text)
        else:
            return text
    
    def items_to_dict(self, items):
        ret = {}
        for k, v in items:
            ret[k] = v
        return ret
    
    def parse_result(self, req):
        if req.status_code < 200 or req.status_code > 304:
            raise Exception('Http connection error: %d', req.status_code)

        et = ET.fromstring(req.text)
        self.ret = {'result': self.items_to_dict(et.items()),
                    'items': [self.items_to_dict(element.items()) for element in et.findall('Item')]}
    
    def request(self, url, data):
        req = requests.post(url, data=data)
        self.parse_result(req)

    def send(self, text, numbers, t=None, **kwargs):
        self.request(url['send'], self.params_send(text, numbers, t, action='sendOnce', **kwargs))
    
    def status(self):
        self.request(url['data'], self.params_auth(action='getSendState'))

    def reply(self):
        self.request(url['data'], self.params_auth(action='getReply'))
    
    def balance(self):
        self.request(url['data'], self.params_auth(action='getBalance'))
    
    def update_key(self, key):
        self.request(url['send'], self.params_auth(action='update'))
        if self.ret['result'] == 1:
            self.authkey = self.ret['items'][0]['authkey']


c = C123()
c.setup('1001@500920850001', '2423E1649E2222DDC82B7027BBE1A7D1', '52', '博而济')

send = c.send
status = c.status
reply = c.reply
balance = c.balance

number = raw_input("输入电话号码: ")
text = raw_input("输入内容: ")
send(text, number)
print c.ret