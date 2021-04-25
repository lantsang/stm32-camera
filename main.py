'''

File: main.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import machine
import ujson

import bluestone_uart
import bluestone_config

# logging.basicConfig(level = logging.INFO)
# _main_log = logging.getLogger("MAIN")

bs_uart = None
bs_config = None

def start_uart():
    global bs_config
    
    print("Init system configuration file")
    bs_config = bluestone_config.BluestoneConfig('config.json')
    config = bs_config.init_config()
    
    print("Init uart service")
    init_uart(config)

def init_uart(config):
    global bs_uart
    
    bs_uart = bluestone_uart.BlueStoneUart()

    init_one_uart(config, 'uart1')
    
def init_one_uart(config, name):
    global bs_config, bs_uart
    
    uart_config = bs_config.read_config_by_name(config, name)
    if uart_config is None:
        uart_config = ujson.loads('{"baud_rate":115200,"data_bits":8,"parity":0,"stop_bits":1}')
        bs_config.update_config(name, uart_config)
    bs_uart.start(name, uart_config)
