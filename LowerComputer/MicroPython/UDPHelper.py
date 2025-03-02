from machine import Pin
import network
import socket
import time
import uselect as select


class UDPHelper:
    def __init__(self, ssid="SSID", password="PASSWORD"):
        # 初始化WiFi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print(wlan.active())
        wlan.connect(ssid, password)

        while not wlan.isconnected() and wlan.status() >= 0:
            print("Waiting to connect......")
            time.sleep(1)
        print("Connected!")
        print("ifconfig: ", wlan.ifconfig())

        self.ip = wlan.ifconfig()[0]

        # 初始化UDP套接字
        port = 5000
        UDP_ADDR = ("", port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(UDP_ADDR)
        self.sock.setblocking(0)  # 设置为非阻塞模式

        print(f"Listening on UDP port {port}...")

    # 发送数据的函数
    def send_data(self, message):
        broadcast_address = '255.255.255.255'  # 广播地址
        broadcast_port = 5000
        self.sock.sendto(message.encode('utf-8'), (broadcast_address, broadcast_port))
        print(f"Sent: {message}")

    def receive(self):
        data_flag = False
        data_str = ""
        
        readable, _, _ = select.select([self.sock], [], [], 1)  # 1秒超时
        if readable:
            try:
                buf, addr = self.sock.recvfrom(1024)
                if buf:
                    print(f"Received from {addr}: {buf.decode('utf-8')}")
                    data_flag = True
                    data_str = buf.decode('utf-8')
            except OSError:
                # 非阻塞套接字在没有数据时可能会抛出异常
                data_flag = False
                pass
        else:
            data_flag = False
            # print("No information received.")
        
        return data_str, data_flag
            
    def __del__(self):
        self.sock.close()
        print("Socket closed.")

# examples
# from UDPHelper import UDPHelper

# udp = UDPHelper()
# while 1:
#     data, data_flag = udp.receive()
