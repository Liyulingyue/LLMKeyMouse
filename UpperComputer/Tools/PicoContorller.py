from .udp_helper import create_socket, udp_send

class PicoController(object):
    def __init__(self):
        self.socket_flag = False

    def set_socket(self, host="", port=8083, pico_address="192.168.2.236", pico_port=5000):
        """
        设置socket连接。
        Args:
            host (str): 目标主机地址，默认为空字符串("")，表示监听所有可用的网络接口。
            port (int): 目标端口号，默认为8083。
            pico_address (str): Pico设备的IP地址，默认为"192.168.2.236"。
            pico_port (int): Pico设备的端口号，默认为5000。
        Returns:
            无
        Raises:
            无
        Description:
            此方法用于设置与Pico设备的socket连接。
            它首先保存Pico设备的IP地址和端口号，然后创建一个socket对象，并将其赋值给self.sock。
            最后，将self.socket_flag设置为True，表示socket已初始化并处于活动状态。
        """
        self.pico_ip = pico_address
        self.pico_port = pico_port

        self.sock = create_socket(host, port)

        self.socket_flag = True

    def send_to_pico(self, data):
        """
        向Pico设备发送数据。
        Args:
            data (str): 要发送的数据，应为字节类型。
        Returns:
            bool: 如果发送成功则返回True，否则返回False。
        Raises:
            无
        Description:
            此方法用于向Pico设备发送数据。首先检查self.socket_flag标志，以确定socket是否已初始化并处于活动状态。
            如果self.socket_flag为False，则方法返回False，表示发送失败。
            如果self.socket_flag为True，则使用udp_send函数通过socket发送数据到Pico设备，并返回True表示发送成功。
        Note:
            - 此方法假设udp_send函数已经定义，并且接受socket对象、数据、目标IP地址和端口号作为参数。
            - data参数应为字节类型，因为网络传输的数据需要是二进制格式。
            - 在调用此方法之前，应确保self.pico_ip和self.pico_port已被正确设置。
        """
        if not self.socket_flag:
            return False
        else:
            udp_send(self.sock, data, self.pico_ip, self.pico_port)
            return True

    def close_socket(self):
        """
        关闭socket连接。
        Args:
            无
        Returns:
            无
        Raises:
            无
        Description:
            此方法用于关闭socket连接。首先检查self.socket_flag标志，以确定socket是否已初始化并处于活动状态。
            如果self.socket_flag为True，则关闭socket连接，并将self.socket_flag设置为False，表示socket已不再处于活动状态。
            如果self.socket_flag为False，则不进行任何操作。
        Note:
            - 在调用此方法之前，应确保self.sock是一个有效的socket对象。
            - 关闭socket后，无法再通过该socket进行通信。
        """
        if self.socket_flag:
            self.sock.close()
            self.socket_flag = False

    def get_socket_status(self):
        """
        获取socket的状态。
        Args:
            无
        Returns:
            bool: 如果socket已初始化并处于活动状态，则返回True；否则返回False。
        Raises:
            无
        Description:
            此方法用于获取当前socket的状态。通过返回self.socket_flag的值来判断socket是否已初始化并处于活动状态。
        Note:
            - 此方法不会修改socket的状态或进行任何网络通信。
            - 调用此方法前，无需担心其对socket状态的影响。
        """
        return self.socket_flag