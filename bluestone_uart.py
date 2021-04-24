'''

File: bluestone_uart.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import utime
import ujson
#import logging
import _thread
from machine import UART

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
        self.uart_name_list = ['uart1', 'uart2']
        
        self._init()

    def _init(self):
        self.bs_config = bluestone_config.BluestoneConfig('config.json')
        self.bs_data_config = bluestone_config.BluestoneConfig('data.json')
        self.bs_camera = bluestone_camera.BlueStoneCamera()

    def _handle_cmd(self, key, config):
        try:
            print("Handle command, the key is {}".format(key))
            if key == 'camera':
                self.bs_camera.start_capture()
        except Exception as err:
            print("Cannot handle command for uart, the error is {}".format(err))

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
        restart = False
    
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
                        restart = False
                    else:
                        restart = self.bs_config.check_key_restart(key)
                        if restart:
                            loop = False
                except Exception as err:
                    utime.sleep_ms(300)
                    print("Cannot handle read command for uart, the error is {}".format(err))
            else:
                continue
            utime.sleep_ms(300)

        if restart:
            restart = False
            print("New configuration was received from uart, restarting system to take effect")
            Power.powerRestart()
        else:
            self.restart_uart(name, config)
    
    def uart_read(self, name, config):
        uart = self.init_uart(name, config)
        self._uart_read(name, uart)
    
    def uart_write(self, name, payload):
        try:
            config_data = self.bs_config.read_config()
            config = ujson.loads(config_data)
            uart_config = self.bs_config.get_value(config, name)
            
            uart = self.init_uart(name, uart_config)
            uart.write(payload)
            utime.sleep_ms(1000)
            print("Write payload {} to {}".format(ujson.dumps(payload), name))
        except Exception as err:
            utime.sleep_ms(1000)
            print("Cannot write payload to {}, the error is {}".format(name, err))
        
    def restart_uart(self, name, config):
        print("Try to close {}".format(name))
        uart.close()
        print("{} was closed".format(name))

        if name in self.uart_name_list:
            self.uart_read(name, config)
    
    def init_uart(self, name, config):
        print("Config is {}".format(config))

        port = 1
        if name == 'uart2':
            port = 2

        baud_rate = self.bs_config.get_int_value(config, "baud_rate")
        data_bits = self.bs_config.get_int_value(config, "data_bits")
        parity = self.bs_config.get_int_value(config, "parity")
        rx = self.bs_config.get_int_value(config, "rx")
        tx = self.bs_config.get_int_value(config, "tx")
        stop_bits = self.bs_config.get_int_value(config, "stop_bits")
        time_out = self.bs_config.get_int_value(config, "time_out")

        self.uart_config[name] = {"baud_rate":baud_rate, "data_bits":data_bits, "parity":parity, "rx":rx, "tx":tx, "stop_bits":stop_bits, "time_out":time_out}

        return UART(port, baudrate=baud_rate, bits=data_bits, parity=parity, stop=stop_bits)

    def start(self, name, config):
        if name in self.uart_name_list:
            _thread.start_new_thread(self.uart_read, (name, config))