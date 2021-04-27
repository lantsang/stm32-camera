'''

File: bluestone_common.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import uos
import ure
import ujson
import _thread

class BluestoneCommon(object):
    inst = None

    def __init__(self):
        BluestoneCommon.inst = self

    @staticmethod
    def generate_random_str():
        random_str = ''.join([('0' + hex(ord(uos.urandom(1)))[2:])[-2:] for x in range(8)])
        return random_str
    
    @staticmethod
    def check_file_exist(file_name):
        if not file_name:
            return False
        
        file_list = uos.listdir()
        if file_name in file_list:
            return True
        else:
            return False

    @staticmethod
    def is_url(url):
        #pattern = ure.compile('http[s]://.+')
        return ure.match('https?://.+', url)
    
    @staticmethod
    def is_json(content):
        if not content:
            return False
        try:
            ujson.loads(content)
            return True
        except Exception as err:
            return False
