'''

File: bluestone_camera.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import camera
import machine
import time

# logging.basicConfig(level = logging.INFO)
# _main_log = logging.getLogger("MAIN")

class BlueStoneCamera(object):
    inst = None

    def __init__(self):
        BlueStoneCamera.inst = self
        
        self.file_name = 'number.txt'
        self.led = machine.Pin(4, machine.Pin.OUT)

    def take_one_picture(self, image_file):
        camera.init()
        self.led.on()
        time.sleep(0.5)
        
        buf = camera.capture()
        self.led.off()
        camera.deinit()
        
        with open(image_file, 'wb') as f:
            f.write(buf)

    def start_capture(self):
        time.sleep(5)
    
        number = None
        with open(self.file_name, 'w+') as f:
            number = f.read()
        print('Number is {}'.format(number))
        if not number:
            number = 1

        self.take_one_picture('sd/Image' + str(number) + '.jpg')
    
        new_number = int(number) + 1
        print('New number is {}'.format(new_number))
        with open(self.file_name, 'w') as f:
            f.write(str(new_number))
        #machine.deepsleep()
