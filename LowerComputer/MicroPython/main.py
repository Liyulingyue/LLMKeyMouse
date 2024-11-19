import network
import socket
import time
from machine import Pin, UART

# 配置 UART
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# 配置 LED
led = Pin("LED", Pin.OUT)

# 连接 Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('****', '******')

while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Connected!")
ip_address = wlan.ifconfig()[0]
print(f"MicroPython IP Address: {ip_address}")

# 设置 UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip_address, 5000))

print("Listening on UDP port 5000...")

# 主循环
while True:
    try:
        print("Waiting to receive UDP data...")
        data, addr = sock.recvfrom(1024)
        print(f"Received data: {data} from {addr}")
        message = data.decode('utf-8').strip()
        print(f"Decoded message: '{message}' from {addr}")

        # 将消息发出
        uart.write(message + '\n')

        # 根据消息内容执行操作
        if message == 'DON':
            led.value(1)
            print("LED turned ON")
        elif message == 'DOFF':
            led.value(0)
            print("LED turned OFF")
        else:
            print("Unknown command")
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)