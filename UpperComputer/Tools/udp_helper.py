import socket
import threading

# 作为服务器进行监听
def udp_server(server_socket):
    print(f"UDP server up and listening on {server_socket.getsockname()[0]}:{server_socket.getsockname()[1]}")
    try:
        while True:
            data, addr = server_socket.recvfrom(32)
            print(f"Received {len(data)} bytes from {addr}: {data.decode()}")
    except KeyboardInterrupt:
        print("UDP server is shutting down.")
    finally:
        server_socket.close()

# 创建 socket 对象，默认绑定所有可用接口
def create_socket(host="", port=8083):
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # 绑定端口号
    server_socket.bind((host, port))

    return server_socket

# 发送UDP报文
def udp_send(server_socket, message, broadcast_address='255.255.255.255', broadcast_port=5000):
    # 将消息编码为字节
    broadcast_data = message.encode()
    # 发送广播消息
    server_socket.sendto(broadcast_data, (broadcast_address, broadcast_port))
    print(f"Broadcasted {len(broadcast_data)} bytes to {broadcast_address}:{broadcast_port}")