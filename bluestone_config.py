'''

File: bluestone_config.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import uos
# import logging
import ujson

import bluestone_common

# logging.basicConfig(level = logging.INFO)
# _config_log = logging.getLogger("CONFIG")

class BluestoneConfig(object):
    inst = None

    def __init__(self, file_name):
        self.config_file = file_name
        self.key_list = ['uart0', 'uart1', 'uart2']
        self.restart_key_list = ['uart0', 'uart1', 'uart2']
        
        BluestoneConfig.inst = self
        
    def check_key_restart(self, key):
        if key is None:
            return False
        if key in self.restart_key_list:
            return True
        return False

    def check_key_exist(self, key):
        if key is None:
            return False
        if key in self.key_list:
            return True
        return False

    def get_value(self, config, key):
        if (config is None) or (key is None):
            return None
        keys = config.keys()
        if keys is None:
            return None
        if key in keys:
            return config[key]
        return None

    def get_int_value(self, config, key):
        value = self.get_value(config, key)
        if value is not None:
            return int(config[key])
        return 0

    def get_float_value(self, config, key):
        value = self.get_value(config, key)
        if value is not None:
            return float(config[key])
        return 0.0

    def init_config(self):
        config = None

        exist = bluestone_common.BluestoneCommon.check_file_exist(self.config_file)
        if exist:
            config = self.read_config()
            print("Read config from {}, the content is {}".format(self.config_file, config))
        else:
            self.create_config()
            print("Config {} does not exist, creating a new one".format(self.config_file))
    
        return config

    def create_config(self):
        path = self.config_file.replace(':', '')
        with open(path, 'w') as f:
            f.write("{}")

    def read_config(self):
        path = self.config_file.replace(':', '')
        content = None
        with open(path, 'r') as f:
            content = f.read()
        return content

    def read_config_by_name(self, config, name):
        if config is None:
            config = '{}'
        current_config = None
        system_config = ujson.loads(config)
        if name in system_config.keys():
            current_config = system_config[name]
        return current_config

    def update_config(self, name, params):
        path = self.config_file
        path = path.replace(':', '')

        content = self.read_config()
        config = ujson.loads(content)

        self.write_config(config, name, params)

    def write_config(self, config, name, params):
        if config == None:
            config = {}
        config[name] = params

        path = self.config_file.replace(':', '')
        new_config = ujson.dumps(config)

        with open(path, 'w') as f:
            print("New config is {}".format(new_config))
            f.write(new_config)
        