import board
import busio
import time
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import digitalio

# 初始化 UART，波特率设为 115200
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)


mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)

# 配置 LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# 指令转化，函数执行映射
def handle_move_right():
    mouse.move(x=10)
    keyboard.press(Keycode.RIGHT)
    keyboard.release_all()

def handle_move_left():
    mouse.move(x=-10)


def handle_led_on():
    print("LED ON command received")

def handle_led_off():

    print("LED OFF command received")


while 1:
    # 读取数据
    in_waiting = uart.in_waiting
    print(in_waiting)
    if uart.in_waiting:
        data = uart.read(uart.in_waiting)
        print(f"Read command: '{data}'")  # 打印接收命令
        # 将数据解码为字符串并打印
        transfer = data.decode().strip()  # 解码
        print(f"Decoded transfer: {transfer}")
        if transfer == "move_left":
            print("Moving mouse left")
            mouse.move(x=-10)  # 向左移动 10 个像素
        elif transfer == "move_right":
            print("Moving mouse right")
            mouse.move(x=10)  # 向右移动 10 个像素
        else:
            print("Unknown command received")
            # 命令无效
    else:
        print("no data")
        time.sleep(1)
