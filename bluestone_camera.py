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
        
        self.file_name = 'capture.jpg'
        self.led = machine.Pin(4, machine.Pin.OUT)

    def take_one_picture(self, image_file):
        camera.init()
        
        self.led.on()
        time.sleep_ms(500)
        
        buf = camera.capture()
        self.led.off()

        with open(image_file, 'wb') as f:
            f.write(buf)
            
        camera.deinit()

    def start_capture(self):
        time.sleep_ms(5000)
        self.take_one_picture(self.file_name)
        #machine.deepsleep()
