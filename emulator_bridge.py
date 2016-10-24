import asynchat
import asyncore
import logging
import socket
from queue import Queue
import threading
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

class luasocket_client(asynchat.async_chat):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port):
        self.received_data = b''
        self.logger = logging.getLogger('luasocket_client')
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (host, port))
        self.set_terminator(TERMINATOR)
        self.connect((host, port))
        self.subs = []
        return

    def handle_connect(self):
        self.logger.debug('handle_connect()')

    def collect_incoming_data(self, data):
        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('collect_incoming_data() -> (%d)\n"""%s"""',
                          len(data), data)
        self.received_data = self.received_data + data

    def found_terminator(self):
        self.logger.debug('found_terminator()')
        received_message = self.received_data
        self.received_data = b''
        for sub in self.subs:
            sub(received_message)
        return

    def add_subscriber(self, func):
        self.logger.debug('added subscriber {0}'.format(func))
        self.subs.append(func)

    def send_msg(self, msg):
        self.push(msg.encode())
        self.push(TERMINATOR)


class emulator_bridge(object):
    def __init__(self, host, port):
        self.logger = logging.getLogger('emulator_bridge')
        self.luasocket_client = luasocket_client(host, port)
        self.luasocket_client.add_subscriber(self.new_data)
        self.in_queue = Queue()
        self.thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        self.luasocket_client.close()
        self.thread.join()

    def new_data(self, msg):
        self.in_queue.put(msg)

    def send_command(self, command, *args):
        command = chr(COMMAND_ENCODINGS[command])
        send_string = command
        for arg in args:
            send_string = send_string + '_' + str(arg)
        self.luasocket_client.send_msg(send_string)
        response = self.in_queue.get(block=True, timeout=8)
        return response

    def frame_advance(self):
        self.send_command('frameadvance')

    def load_state(self, state):
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
            return self.send_command("readbytes", startaddress, length)
        elif stopaddress:
            return self.send_command("readbytes", startaddress, stopaddress-startaddress + 1)
        else:
            raise Exception("No length or stop address given")

    def read_many_bytes(self, addresslist):
        """Addresslist format is [address,length,address,length], ie [0x02,2,0x03,1]"""
        return self.send_command("readbytes", *addresslist)
