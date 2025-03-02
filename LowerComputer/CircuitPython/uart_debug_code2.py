import board
import busio
import time

# 初始化UART，波特率设为115200
# uart = busio.UART(board.TX, board.RX, baudrate=115200)
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)
data_cache = ""

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
        # 清空缓存，准备接收下一批数据
        data_cache = received_data_list[-1]  # 保留"[EBD]"之后的部分（如果有的话）