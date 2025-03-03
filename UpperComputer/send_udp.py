import socket

def main():
    server_ip = '192.168.2.244'
    server_port = 5000

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = input("Enter message to send: ")
        if message.lower() == 'exit':
            break
        data = message.encode('utf-8')
        udp_socket.sendto(data, (server_ip, server_port))
        print(f"Sent {len(data)} bytes to {server_ip}:{server_port}")

if __name__ == '__main__':
    main()
