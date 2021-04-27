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
        
        self.image_file_name = 'capture'
        self.image_file = self.image_file_name + '.jpg'
        self.led = machine.Pin(4, machine.Pin.OUT)

    def get_image_file_name(self):
        return self.image_file_name
    
    def get_image_file(self):
        return self.image_file

    def take_one_picture(self):
        try:
            camera.init()
            
            self.led.on()
            time.sleep_ms(500)
            
            buf = camera.capture()
            self.led.off()
            
            with open(self.image_file, 'wb') as f:
                f.write(buf)
        except Exception as err:
            print("Cannot save one picture to {}, the error is {}".format(self.image_file, err))
        finally:
            camera.deinit()
       
    def start_capture(self):
        #time.sleep_ms(5000)
        self.take_one_picture()
        #machine.deepsleep()
