import socket
import struct

CMD_CONNECT = 1000
CMD_EXIT = 1001
CMD_DISABLEDEVICE = 1003
CMD_ENABLEDEVICE = 1004
CMD_GETUSERINFO = 9
CMD_SETUSERINFO = 8

class ZK:
    def __init__(self, ip, port=4370, timeout=5):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.ip, self.port))
        self._send_command(CMD_CONNECT)
        return self

    def disconnect(self):
        if self.sock:
            self._send_command(CMD_EXIT)
            self.sock.close()
            self.sock = None

    def disable_device(self):
        self._send_command(CMD_DISABLEDEVICE)

    def enable_device(self):
        self._send_command(CMD_ENABLEDEVICE)

    def get_users(self):
        # Dummy simple users list (in real project, replace with real parsing)
        return []  # You can integrate reading later if needed

    def set_user(self, uid, name, privilege=0, password='', group_id='', user_id=None):
        """
        Adds a user to the device.
        """
        # Simplified example. In real world, you would have to format the packet
        print(f"Simulated: Set user UID={uid}, Name={name}")

    def _send_command(self, command):
        if not self.sock:
            raise Exception("Device not connected")
        buf = struct.pack('HHHH', command, 0, 0, 0)
        self.sock.send(buf)
