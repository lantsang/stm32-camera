import os
import camera
import machine
import time

led = machine.Pin(4, machine.Pin.OUT)

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

def start():
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
