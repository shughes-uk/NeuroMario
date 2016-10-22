import subprocess
import socket
import struct
import asynchat
import logging
import asyncore

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s: %(message)s',)


class emu_client(asynchat.async_chat):
    """Sends messages to the server and receives responses.
    """

    def __init__(self, host, port):
        self.received_data = b''
        self.logger = logging.getLogger('EchoClient')
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', (host, port))
        self.set_terminator('\n\r\n\r'.encode())
        self.connect((host, port))
        self.subs = []
        return

    def handle_connect(self):
        self.logger.debug('handle_connect()')

    def collect_incoming_data(self, data):
        """Read an incoming message from the client and put it into our outgoing queue."""
        self.logger.debug('collect_incoming_data() -> (%d)\n"""%s"""', len(data), data)
        self.received_data = self.received_data + data

    def found_terminator(self):
        self.logger.debug('found_terminator()')
        received_message = self.received_data
        self.received_data = b''
        for sub in self.subs:
            sub(self, received_message)
        return

    def add_subscriber(self, func):
        self.logger.debug('added subscriber {0}'.format(func))
        self.subs.append(func)


def got_data(client, data):
    # print (data)
    mem_requests = []
    from mariolocs import locations
    for location in locations:
        if type(location[1]) is tuple:
            start = location[1][0]
            end = location[1][1]
        else:
            start = location[1]
            end = start
        request = "{0}_{1}".format(start, end - start + 1)
        mem_requests.append(request)

    # print(','.join(mem_requests))
    eclient.push(','.join(mem_requests).encode())
    eclient.push('\n'.encode())
    print(data)
    #     x = struct.unpack("H", data[0:2])[0]
    #     y = struct.unpack("H", data[2:4])[0]
    #     state = struct.unpack("H", data[4:6])[0]
    #     print(x, y, state)
    #     client.push("\n".encode())
    # except:
    #     pass


FCEUX_BIN = "FCEUX/fceux.exe"
LUA_RELAY_PATH = "hawk_api.lua"
ROM_PATH = "Super Mario Bros. (JU) (PRG0) [!].nes"
SAVE_STATE_PATH = "level_1_state.fc0.fcs"
proc = subprocess.Popen([FCEUX_BIN, "-lua", LUA_RELAY_PATH, '-loadstate', SAVE_STATE_PATH, ROM_PATH])
eclient = emu_client('127.0.0.1', 9000)
eclient.add_subscriber(got_data)
eclient.push('0x0001_3,0x5_5'.encode())
eclient.push('\n'.encode())
try:
    asyncore.loop()
finally:
    proc.terminate()
# proc.terminate()
