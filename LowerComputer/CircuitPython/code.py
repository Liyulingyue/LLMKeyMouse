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

# 初始化UART，波特率设为115200
# uart = busio.UART(board.TX, board.RX, baudrate=115200)
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)
data_cache = ""

# 初始化鼠标和键盘
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.LED)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT

def mouse_action(command_str):
    # mouse.move(x=1)
    # mouse.move(y=1)
    # mouse.click(Mouse.LEFT_BUTTON)
    command_list = command_str.split(':')
    if command_list[1][0] == 'x':
        mouse.move(x=int(command_list[2]))
    elif command_list[1][0] == 'y':
        mouse.move(y=int(command_list[2]))
    elif command_list[1][0] == 'c':
        mouse.click(Mouse.LEFT_BUTTON)
    else:
        print(f"No matched keywords in {command_str}")
        pass

def keyboard_action(command_str):
    command_list = command_str.split(':')
    if command_list[1][0] == 's': # string
        input_string = ":".join(command_list[2:])
        keyboard_layout.write(input_string)
    else:
        # keyboard.press(control_key, key)  # "Press"...
        # keyboard.release_all()  # ..."Release"!
        print(f"No matched keywords in {command_str}")

def execute_command(command_str):
    # 若长度过低，首字母为I，则为无效数据（I为内部数据）
    if len(command_str) < 1:
        pass
    elif command_str[0] == 'I': # 内部数据标识
        pass
    elif command_str[0] == 'M': # 鼠标操作
        mouse_action(command_str)
    elif command_str[0] == 'K': # 键盘操作
        keyboard_action(command_str)
    else:
        print(f"No matched keywords in {command_str}")

while 1:
    # 读取数据，如果有的话
    in_waiting = uart.in_waiting
    if uart.in_waiting:
        data = uart.read(uart.in_waiting)
        # print(data)
        # 将数据解码为字符串并打印
        print(f"INNER_RECEIVE: {data.decode()}")
        data_cache += data.decode()
    else:
        # print("no data")
        time.sleep(0.1)

    # 检查是否包含"[END]"
    if "[END]" in data_cache:
        # 提取"[EBD]"之前的数据
        received_data_list = data_cache.split("[END]")
        # 打印接收到的数据
        for string in received_data_list[:-1]:
            print("Received data:", string)
            try:
                execute_command(string)
            except:
                print("error with {}".format(string))

        # 清空缓存，准备接收下一批数据
        data_cache = received_data_list[-1]  # 保留"[EBD]"之后的部分（如果有的话）
