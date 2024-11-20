import socket
from utils import LOG
from llm.erniebot import Ernie_TransChain


def main():
    server_ip = '192.168.1.12'
    server_port = 5000

    model_name = "ernie-4.0"
    access_token = "api_key"

    # 创建 Ernie_TransChain
    ernie_trans_chain = Ernie_TransChain(model_name=model_name, access_token=access_token)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        # 获取用户输入
        message = input("Enter message to send: ")
        if message.lower() == 'exit':
            break

        # few-shot
        few_shot = "输出示例为：('input','向右移动10个','trans_result','move(x=10)')"
        response, success = ernie_trans_chain.run(message, few_shot)
        if success:
            # 通过 UDP 发送数据
            data = response.encode('utf-8')
            udp_socket.sendto(data, (server_ip, server_port))
            print(f"Sent {len(data)} bytes to {server_ip}:{server_port}")
        else:
            print(f"Error in processing input: {response}")


if __name__ == '__main__':
    main()
