'''

File: common.py

Project: bluestone

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
