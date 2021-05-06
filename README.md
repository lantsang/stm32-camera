##  前言
本文的主要说明如何通过移远EC600S和ESP32-CAM来实现远程拍照抄表的功能。这套方案针对的是对现有传统燃气表、水表和其他仪表的智能化改造，在不需要更换表的前提下实现远程抄表功能。


- **[硬件平台](#jump_1)**
- **[连接图](#jump_2)**
- **[架构图](#jump_3)**
- **[运行环境](#jump_4)**
- **[实拍照片](#jump_4)**
- **[未完待续](#jump_5)**
- **[参考链接](#jump_6)**

<a id="jump_1"></a>
## 1 硬件平台
代码分别运行在移远的EC600S和ESP32-CAM上，ESP32-CAM负责拍照和发送图片数据，EC600S负责接收数据并将数据转发给软件平台，软件平台最终负责将各部分图片数据合成一张照片，合成后的照片再调用百度图片识别服务进行识别。嵌入式平台的开发语言分别是QuecPython和MicroPython，由于QuecPython派生自MicroPython，所以实际开发的时候差别并不大。

![EC600S](https://bluestone.oss-cn-beijing.aliyuncs.com/images/1.%20EC600S.jpeg)

![ESP32-CAM](https://bluestone.oss-cn-beijing.aliyuncs.com/images/ESP32-CAM.jpeg)

<a id="jump_2"></a>
## 2 连接图
![连接图](https://bluestone.oss-cn-beijing.aliyuncs.com/images/4.%20EC600S%E4%B8%8EESP32-CAM%E8%BF%9E%E6%8E%A5%E5%9B%BE.png)

| EC600S   | ESP32-CAM | 备注 |
| :-----: | :--: | :------------: |
| MISO |  GPIO14  | 串口接收-发送 |
| MOSI |  GPIO13  | 串口发送-接收 |

以上是串口线的连接，EC600S和ESP32-CAM还需要分别接入5V电源和地。

<a id="jump_3"></a>
## 3 架构图
![系统架构图](https://bluestone.oss-cn-beijing.aliyuncs.com/images/3.%20%E7%B3%BB%E7%BB%9F%E6%A1%86%E6%9E%B6%E5%9B%BE.png)

1. 由定时器或者软件后台下发指令给EC600S；
2. EC600S通过MQTT接收到拍照指令以后再将指令通过串口发送给ESP32-CAM；
3. ESP32-CAM接收到指令后开始拍照，并将照片存储到本地FLASH上；
4. ESP32-CAM以1024个字节为一个单位将图片数据通过串口分包发给EC600S；
5. EC600S将接收到的数据包发给软件后台；
6. EC600S发送结束指令给软件后台，软件后台以a附加的形式向文件中写入；
7. 软件后台接收到结束指令以后开始调用百度云服务进行图片识别；
8. 保存识别结果备用。

<a id="jump_4"></a>
## 4 运行环境
### 4.1 EC600S
具体代码导入步骤参考[移远EC600 SmartDtu 说明文档](https://gitee.com/lantsang/smart-dtu)
### 4.2 ESP32-CAM
#### 4.2.1 安装esptool
```bash
pip install esptool
```
#### 4.2.2 引导模式
将USB转TTL串口转换器连接到ESP32-CAM开发板上，并将IO0和地连接起来，这样就可以进入引导模式

#### 4.2.3 格式化ESP32-CAM
按一下RST键，然后执行如下命令来擦除ESP32-CAM的Flash
```bash
esptool.py --port COM27 erash_flash
```
> 注：Windows下COM27要根据实际端口号替换，Linux下为/dev/ttyUSB0

#### 4.2.4 刷入固件
进入固件所在的目录，然后按一下RST按钮，之后执行如下命令：
```bash
esptool.py --chip esp32 --port COM27 --baud 460800 write_flash -z 0x1000 ESP32CAM_fireware.bin
```
现在固件已经刷入ESP32-CAM开发板上了，断开IO0与地之间的连接，然后再按一次RST按钮

#### 4.2.5 安装ampy工具
```bash
pip install adafruit-ampy
```

#### 4.2.6 下载应用代码
```bash
git clone https://gitlab.lantsang.cn/bluestone/bs-stm32-camera.git
```

#### 4.2.7 将应用代码下载到ESP32-CAM开发板
```bash
ampy --port COM27 put boot.py
ampy --port COM27 put main.py
ampy --port COM27 put bluestone_camera.py
ampy --port COM27 put bluestone_common.py
ampy --port COM27 put bluestone_uart.py
```

#### 4.2.8 启动应用程序
直接再按一次RST键，ESP32-CAM上的应用程序就会自动开始运行

#### 4.2.9 下发指令
打开软件后台，找到注册上来并在线的设备，然后选择UART1，在消息窗口输入：
```json
{"capture": 1}
```
然后点击发送即可

<a id="jump_5"></a>
## 5 实拍照片
服务器接收到照片以后会保存在public/images目录下，照片示例如下：

![实拍照片](https://bluestone.oss-cn-beijing.aliyuncs.com/images/5.%20ESP32-CAM%20%E5%AE%9E%E6%8B%8D%E7%85%A7%E7%89%87.jpg)

<a id="jump_6"></a>
## 6 未完待续
服务器端需要继续接入百度图像识别服务来得到图片上的数字，并将数据存储到数据库中。

<a id="jump_7"></a>
## 7 参考链接
[移远EC600S SmartDtu](https://gitee.com/lantsang/smart-dtu)

[将ESP32-CAM变成微型摄像头](https://github.com/KipCrossing/Micro-Camera)

[ESP32 rst:0x10 (RTCWDT_RTC_RESET)](https://blog.csdn.net/toopoo/article/details/98793848)

[json二进制传输方案](https://blog.csdn.net/qq_43203949/article/details/113184314)

[ESP32快速参考手册](https://docs.micropython.org/en/latest/esp32/quickref.html)

[ESP32基础教程](http://www.1zlab.com/wiki/micropython-esp32/)