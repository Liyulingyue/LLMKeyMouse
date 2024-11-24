import socket
from utils import LOG
from llm.erniebot import Ernie_TransChain
import time


def main():
    server_ip = '192.168.1.11'
    server_port = 5000

    model_name = "ernie-bot-4"
    access_token = 'api_key'

    # 创建 Ernie_TransChain
    ernie_trans_chain = Ernie_TransChain(model_name=model_name, access_token=access_token)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        # 获取用户输入
        #鼠标向右移动1000
        message = input("Enter message to send: ")
        if message.lower() == 'exit':
            break

        # few-shot
        commands, success = ernie_trans_chain.run(message)
        if success:
            # 通过 UDP 逐条发送数据
            for command in commands:
                try:
                    # 将单条命令编码为 UTF-8 格式
                    data = command.encode('utf-8')
                    udp_socket.sendto(data, (server_ip, server_port))
                    print(f"Sent {len(data)} bytes: {command} to {server_ip}:{server_port}")
                    LOG.debug(f"Sent {len(data)} bytes: {command} to {server_ip}:{server_port}")

                    # 等待 2 秒
                    time.sleep(2)
                except Exception as e:
                    print(f"Error sending command {command}: {e}")
                    LOG.error(f"Error sending command {command}: {e}")
        else:
            # 如果失败，打印错误信息
            print(f"Error in processing input: {commands}")
            LOG.error(f"Error in processing input: {commands}")


if __name__ == '__main__':
    main()
