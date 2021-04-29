'''

File: bluestone_uart.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import uos
import machine
import utime
import ujson
import ubinascii
#import logging
import _thread
from machine import UART

import bluestone_common
import bluestone_config
import bluestone_camera

# logging.basicConfig(level = logging.INFO)
# _uart_log = logging.getLogger("UART")

class BlueStoneUart(object):
    inst = None

    def __init__(self):
        BlueStoneUart.inst = self

        self.bs_config = None
        self.bs_data_config = None
        self.bs_camera = None
        self.uart_config = {}
        self.uart_name_list = ['uart2']
        self.uart_list = {}
        
        self._init()

    def _init(self):
        self.bs_config = bluestone_config.BluestoneConfig('config.json')
        self.bs_data_config = bluestone_config.BluestoneConfig('data.json')
        self.bs_camera = bluestone_camera.BlueStoneCamera()

    def _handle_cmd(self, key, config):
        try:
            print("Handle command, the key is {}".format(key))
            if key == 'capture':
                self.bs_camera.start_capture()
                uart_name = None
                if self.uart_name_list and len(self.uart_name_list) > 0:
                    uart_name = self.uart_name_list[0]
                if uart_name:
                    self.send_image(uart_name)
                    print("Write image binary to {}".format(uart_name))
        except Exception as err:
            print("Cannot handle command for uart, the error is {}".format(err))

    def send_image_end_flag(self, uart_name, image_file_name):
        message = {'image':{}}
        message['image']['image_file'] = image_file_name
        message['image']['image_end'] = True
                        
        self.uart_write(uart_name, ujson.dumps(message))
    
    def send_image(self, uart_name):
        image_file_name = self.bs_camera.get_image_file_name()
        image_file = self.bs_camera.get_image_file()
        random_image_file = '{}_{}.jpg'.format(image_file_name, bluestone_common.BluestoneCommon.generate_random_str())
        try:
            with open(image_file, 'rb') as f:
                while True:
                    raw_data = f.read(1024) #1024 * 7
                    if raw_data and len(raw_data) > 0:
                        message = {'image':{}}
                        message['image']['image_file'] = random_image_file
                        # base64编码，生成新的可字符化的二进制序列
                        base64_data = ubinascii.b2a_base64(raw_data)
                        # 字符串化，使用utf-8的方式解析二进制
                        base64_str = str(base64_data, 'utf-8')
                        message['image']['image_binary'] = base64_str
                        
                        self.uart_write(uart_name, ujson.dumps(message))
                    if not raw_data or len(raw_data) < 1024:
                        break
                    utime.sleep_ms(300)
            self.send_image_end_flag(uart_name, random_image_file)
        except Exception as err:
            print("Cannot read {}, the error is {}".format(image_file, err))

    def check_key_exist(self, key):
        if key is None:
            return False
        if key in self.key_list:
            return True
        return False

    def _uart_read(self, name, uart):
        print("UART {} start with {}".format(name, uart))
        config = None
        loop = True
    
        while loop:
            num = uart.any()
            utime.sleep_ms(50)
            num2 = uart.any()
            if num != num2:
                continue

            if num:
                print("UART ready data length is {}".format(num))
                msg = uart.read(num)
                # 初始数据是字节类型（bytes）,将字节类型数据进行编码
                utf8_msg = msg.decode()
                print("UART read message is {}".format(utf8_msg))

                try:
                    config_setting = ujson.loads(utf8_msg)
                    config_keys = config_setting.keys()
                    if 'payload' in config_keys: # uart write payload, ignore it
                        continue
                    for key in config_setting:
                        config = config_setting[key]
                        exist = self.bs_config.check_key_exist(key)
                        if exist:
                            self.bs_config.update_config(key, config)
                        self._handle_cmd(key, config)
                    if name in config_keys:
                        config = config_setting[name] # 保证重启逻辑的数据正确性
                        loop = False
                except Exception as err:
                    utime.sleep_ms(50)
                    print("Cannot handle read command for uart, the error is {}".format(err))
            else:
                utime.sleep_ms(50)
                continue
            utime.sleep_ms(50)

        if config:
            self.restart_uart(name, config)
    
    def uart_read(self, name, config):
        uart = self.init_uart(name, config)
        self._uart_read(name, uart)
    
    def uart_write(self, name, data):
        try:
            uart = self.uart_list[name]
            if uart:
                uart.write(data)
                print("Write {} bytes to {}".format(len(data), name))
                utime.sleep_ms(1000)
        except Exception as err:
            utime.sleep_ms(1000)
            print("Cannot write data to {}, the error is {}".format(name, err))
        
    def restart_uart(self, name, config):
        print("Try to close {}".format(name))
        uart.close()
        print("{} was closed".format(name))

        if name in self.uart_name_list:
            self.uart_read(name, config)
    
    def init_uart(self, name, config):
        print("Config is {}".format(config))

        port = 0
        if name == 'uart1':
            port = 1
        elif name == 'uart2':
            port = 2

        baud_rate = self.bs_config.get_int_value(config, "baud_rate")
        data_bits = self.bs_config.get_int_value(config, "data_bits")
        parity = self.bs_config.get_int_value(config, "parity")
        stop_bits = self.bs_config.get_int_value(config, "stop_bits")

        self.uart_config[name] = {"baud_rate":baud_rate, "data_bits":data_bits, "parity":parity, "stop_bits":stop_bits}

        uart = UART(port, baudrate=baud_rate, tx=14, rx=13, timeout=10)
        self.uart_list[name] = uart
        
        return uart

    def start(self, name, config):
        if name in self.uart_name_list:
            _thread.start_new_thread(self.uart_read, (name, config))