import logging
import socket
import struct
TERMINATOR = '\r\n'.encode()
COMMAND_ENCODINGS = {
                    "frameadvance": 0x01,
                    "speedmode_maximum": 0x02,
                    "speedmode_normal": 0x03,
                    "message": 0x04,
                    "framecount": 0x05,
                    "emulating": 0x06,
                    "print": 0x07,
                    "readbyte": 0x08,
                    "readbytesigned": 0x09,
                    "readbytes": 0x10,
                    "joypadset": 0x11,
                    "loadstate": 0x12
}

class luasocket_client(object):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port):
        self.logger = logging.getLogger('luasocket_client')
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (host, port))
        self.socket.connect((host, port))
        #self.socket.sendall(TERMINATOR)
        return

    def close(self):
        self.socket.close()

    def add_subscriber(self, func):
        self.logger.debug('added subscriber {0}'.format(func))
        self.subs.append(func)

    def send_msg(self, msg):
        self.socket.sendall(msg.encode() + TERMINATOR)
        terminator_received = False
        response = b''
        while not terminator_received:
            response += self.socket.recv(1)
            if response[-2:] == b'\r\n':
                terminator_received = True
        #print (response)
        return response[:-2]



class emulator_bridge(object):
    def __init__(self, host, port):
        self.logger = logging.getLogger('emulator_bridge')
        self.luasocket_client = luasocket_client(host, port)
        self.send_command("speedmode_maximum")

    def __del__(self):
        self.luasocket_client.close()

    def new_data(self, msg):
        self.in_queue.put(msg)

    def send_command(self, command, *args):
        command = chr(COMMAND_ENCODINGS[command])
        send_string = command
        for arg in args:
            send_string = send_string + '_' + str(arg)
        response = self.luasocket_client.send_msg(send_string)
        return response

    def frame_advance(self):
        self.send_command('frameadvance')

    def load_state(self, state):
        print("send load")
        self.send_command('loadstate', state)

    def message(self, message):
        self.send_command("message", message)

    def get_framecount(self):
        count = self.send_command("framecount")
        return int(count)

    def get_emulating(self):
        emulating = self.send_command("emulating")
        return bool(emulating)

    def lua_print(self, message):
        self.send_command("print", message)

    def read_bytes(self, startaddress, length=None, stopaddress=None):
        if length:
            byte_array = self.send_command("readbytes", startaddress, length)
            return list(struct.unpack('{0}B'.format(len(byte_array)), byte_array))
        elif stopaddress:
            byte_array = self.send_command("readbytes", startaddress, stopaddress-startaddress + 1)
            return list(struct.unpack('{0}B'.format(len(byte_array)), byte_array))
        else:
            raise Exception("No length or stop address given")

    def read_many_bytes(self, addresslist):
        """Addresslist format is [address,length,address,length], ie [0x02,2,0x03,1]"""
        return self.send_command("readbytes", *addresslist)

    def joypad_set(self, joypad):
        return self.send_command("joypadset", '_'.join(str(x) for x in joypad))
