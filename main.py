import os
import camera
import machine
import time
import ujson

import bluestone_uart
import bluestone_config

# logging.basicConfig(level = logging.INFO)
# _main_log = logging.getLogger("MAIN")

led = machine.Pin(4, machine.Pin.OUT)
bs_uart = None
bs_config = None

def start_uart():
    global bs_config
    
    # _main_log.info("Init system configuration file")
    bs_config = bluestone_config.BluestoneConfig('config.json')
    config_data = bs_config.init_config()
    
    # _main_log.info("Init uart service")
    init_uart(config_data)

def init_uart(config):
    global bs_uart
    
    bs_uart = bluestone_uart.BlueStoneUart()

    init_one_uart(config, 'uart1')
    init_one_uart(config, 'uart2')
    
def init_one_uart(config, name):
    global bs_config, bs_uart
    
    uart_config = bs_config.read_config_by_name(config, name)
    if uart_config is None:
        uart_config = ujson.loads('{"baud_rate":115200,"data_bits":8,"parity":0,"rx":14,"tx":15,stop_bits":1,"time_out":0}')
        bs_config.update_config(name, uart_config)
    bs_uart.start(name, uart_config)

def take_one_picture(tnumber_file):
    camera.init()
    led.on()
    time.sleep(0.5)
    buf = camera.capture()
    led.off()
    camera.deinit()
    f = open(tnumber_file, 'wb')
    f.write(buf)
    f.close()

def start_capture():
    time.sleep(5)
    
    path = 'number.txt'
    number = None
    with open(path) as f:
        number = f.read()
    print('Number is {}'.format(number))
    if not number:
        number = 1

    take_one_picture('sd/Image' + str(number) + '.jpg')
    
    new_number = int(number) + 1
    print('New number is {}'.format(new_number))
    with open(path, 'w') as f:
        f.write(str(new_number))

    #machine.deepsleep()
