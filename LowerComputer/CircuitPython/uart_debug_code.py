import board
import busio
import time

# 初始化UART，波特率设为115200
# uart = busio.UART(board.TX, board.RX, baudrate=115200)
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

while 1:
    # 读取数据，如果有的话
    in_waiting = uart.in_waiting
    print(in_waiting)
    if uart.in_waiting:
        data = uart.read(uart.in_waiting)
        print(data)
        # 将数据解码为字符串并打印
        print(data.decode())
    else:
        print("no data")
        time.sleep(0.1)