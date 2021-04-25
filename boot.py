'''

File: boot.py

Project: bluestone esp32 camera

Author: daniel dong

Email: dongzhenguo@lantsang.cn

Copyright 2021 - 2021 bluestone tech

'''

import uos
import machine
import main

uos.mount(machine.SDCard(), "/sd")
main.start_uart()