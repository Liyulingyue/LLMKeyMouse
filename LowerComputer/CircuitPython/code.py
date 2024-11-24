import board
import busio
import time
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
import usb_hid
import digitalio
import json
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# 初始化 UART，波特率设为 115200
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

# 初始化鼠标和键盘
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.LED)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT


def execute_command(command_type, operation_type, payload):
    """
    根据解析的命令执行对应操作。
    """
    try:
        if command_type == "0":  # Mouse
            if operation_type == "1":  # Move
                direction = payload[0]
                steps = int(payload[1:])

                if direction == "x":
                    mouse.move(x=steps)
                elif direction == "y":
                    mouse.move(y=steps)
                else:
                    print(f"Invalid direction for mouse move: {direction}")
                    return

                print(f"Moved mouse {steps} steps in {direction} direction.")
            elif operation_type == "2":  # Click
                mouse.click(Mouse.LEFT_BUTTON)  # 点击鼠标左键
                print("Mouse clicked.")
            else:
                print(f"Unknown mouse operation: {operation_type}")

        elif command_type == "1":  # Keyboard
            if operation_type == "1":  # Write
                text = payload
                keyboard_layout.write(text)  # 输入文本
                print(f"Typed text: {text}")
            else:
                print(f"Unknown keyboard operation: {operation_type}")

        print("Executed command successfully.")

    except Exception as e:
        print(f"Command execution failed: {e}")


def parse_uart_data(data):
    """
    解析从 UART 接收到的字符串命令。
    """
    try:
        # 检查数据长度
        if len(data) < 4:
            raise ValueError("Command too short to parse.")

        # 按协议解析命令
        command_type = data[0]  # 第一个字符表示设备类型
        # 先跳过 length_flag 的验证
        operation_type = data[3]  # 第四字符表示操作类型
        command_payload = data[4:]  # 剩余部分为指令载荷

        return command_type, operation_type, command_payload

    except Exception as e:
        print(f"Failed to parse UART data: {e}")
        return None, None, None


while True:
    if uart.in_waiting:
        try:
            raw_data = uart.read(uart.in_waiting).decode("utf-8").strip()
            print(f"Received data: {raw_data}")

            # 解析命令
            command_type, operation_type, payload = parse_uart_data(raw_data)
            if command_type and operation_type:
                # 执行解析的命令
                execute_command(command_type, operation_type, payload)
            else:
                print("Invalid command received.")
        except Exception as e:
            print(f"Error reading UART data: {e}")
    else:
        time.sleep(0.1)  # 等待下一个指令