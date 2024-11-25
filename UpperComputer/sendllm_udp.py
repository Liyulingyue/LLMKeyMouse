import socket
from utils import LOG
from llm.erniebot import Ernie_TransChain
import time
from speech2txt.speech_to_text import SpeechToText



def process_speech_to_text(stt):
    """
    录音并将语音转换为文本。
    :param stt: SpeechToText 实例
    :return: 识别到的文本，或 None（如果失败）
    """
    try:
        # 提示用户录音开始
        print("Recording your message... Press 's' and Enter to stop.")

        # 调用录音功能
        audio_file = stt.record_audio()
        print(f"Audio recorded and saved to: {audio_file}")

        # 检查录音文件是否生成
        import os
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            raise ValueError("Recorded audio file is empty or missing.")

        # 调用语音识别功能
        print("Converting speech to text...")
        message = stt.recognize_speech(file_path=audio_file)
        if not message or not isinstance(message, str):
            raise ValueError("Speech recognition returned empty or invalid result.")

        # 返回识别结果
        print(f"Recognized message: {message}")
        return message

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        LOG.error(f"Validation Error: {ve}")
    except FileNotFoundError as fe:
        print(f"File Error: {fe}")
        LOG.error(f"File Error: {fe}")
    except Exception as e:
        print(f"Error during speech-to-text processing: {e}")
        LOG.error(f"Unhandled Error during speech-to-text processing: {e}")

    # 如果发生异常，返回 None
    return None


def main():
    command_delay=2
    server_ip = '192.168.1.10'
    server_port = 5000

    model_name = "ernie-bot-4"
    access_token = 'api_key'

    # 创建 Ernie_TransChain
    ernie_trans_chain = Ernie_TransChain(model_name=model_name, access_token=access_token)
    # 替换为实际的百度 API_KEY 和 SECRET_KEY
    Audio_API_KEY = "api_key"
    SECRET_KEY = "secret_key"
    try:
        # 初始化 SpeechToText 类
        stt = SpeechToText(Audio_API_KEY, SECRET_KEY)
    except Exception as e:
        print(f"Error initializing SpeechToText: {e}")
        LOG.error(f"Error initializing SpeechToText: {e}")
        exit(1)


    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # 主循环
        while True:
            print("Press Enter to start recording your message (or type 'exit' to quit).")
            user_input = input().strip().lower()
            if user_input == 'exit':
                print("Exiting program. Goodbye!")
                LOG.info("User exited the program.")
                break

            # 调用语音转文字
            try:
                message = process_speech_to_text(stt)
                if not message:
                    print("Speech recognition failed. Please try again.")
                    LOG.error("Speech recognition returned None or invalid message.")
                    continue
                print(f"Recognized message: {message}")
            except Exception as e:
                print(f"An error occurred during speech-to-text processing: {e}")
                LOG.error(f"Speech-to-text error: {e}")
                continue

            # 检查语音内容是否要求退出
            if message.lower() == 'exit':
                print("Exiting program. Goodbye!")
                LOG.info("User exited the program via speech command.")
                break

            # Few-shot
            try:
                commands, success = ernie_trans_chain.run(message)
                if not success or not commands or not all(isinstance(cmd, str) for cmd in commands):
                    print("No valid commands generated. Please try again.")
                    LOG.error(f"Invalid commands received: {commands}")
                    continue
            except Exception as e:
                print("An error occurred while processing the input. Please try again.")
                LOG.error(f"Error in ernie_trans_chain.run(): {e}")
                continue

            # 发送命令通过 UDP
            for command in commands:
                try:
                    data = command.encode('utf-8')
                    udp_socket.sendto(data, (server_ip, server_port))  # 使用直接定义的变量
                    print(f"Sent {len(data)} bytes: {command} to {server_ip}:{server_port}")
                    LOG.debug(f"Sent {len(data)} bytes: {command} to {server_ip}:{server_port}")
                    time.sleep(command_delay)  # 使用直接定义的延迟变量
                except Exception as e:
                    print(f"Error sending command {command}: {e}")
                    LOG.error(f"Error sending command {command}: {e}")

    finally:
        try:
            udp_socket.close()
            print("Socket closed. Exiting program.")
            LOG.info("Socket closed and program exited.")
        except Exception as e:
            print(f"Error while closing socket: {e}")
            LOG.error(f"Error while closing socket: {e}")


if __name__ == '__main__':
    main()
