# 该文件用于对uart进行debug，会以特定时间间隔发送消息，对应的接受设备会打印出接收到的消息

from machine import UART, Pin
import time

led = Pin("LED", Pin.OUT)
# 初始化UART，波特率设为115200
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

while True:
    # 发送数据
    uart.write("Hello from MicroPython!\n")
    led.value(1)
    time.sleep(0.5)
    print("Hello from MicroPython!\n")
    led.value(0)
    # 等待一段时间再发送下一条消息
    time.sleep(2)