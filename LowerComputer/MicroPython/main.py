import network
import socket
import time
from machine import Pin, UART
from UDPHelper import UDPHelper

# 创建网络连接
udp = UDPHelper(ssid="****", password="****")
# 配置 UART
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
# 配置 LED
led = Pin("LED", Pin.OUT)

# 连接成功，闪烁三次
led.value(1)
time.sleep(0.1)
led.value(0)
time.sleep(0.1)
led.value(1)
time.sleep(0.1)
led.value(0)
time.sleep(0.1)
led.value(1)
time.sleep(0.1)
led.value(0)

uart.write(f"INNER_INFO:{udp.ip}[END]")

# 主循环
while True:
    data_str, data_flag = udp.receive()
    if data_flag:
        if data_str == "LED_ON[END]":
            led.value(1)
            pass
        elif data_str == "LED_OFF[END]":
            led.value(0)
            pass
        else: # 转发
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            pass

        uart.write(data_str)
    else:
        # uart.write("INNER_INFO")
        pass