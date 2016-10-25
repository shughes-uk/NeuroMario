import subprocess
import logging
from emulator_bridge import emulator_bridge
from mariolocs import locations
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s: %(message)s', )


class MarioInterface(object):
    FCEUX_BIN = "../FCEUX/fceux.exe"
    LUA_RELAY_PATH = "hawk_api.lua"
    ROM_PATH = "Super Mario Bros. (JU) (PRG0) [!].nes"
    SAVE_STATE_PATH = "level_1_state.fcs"

    def __init__(self, frame_interval=5, operating_port=9001,):
        self.proc = subprocess.Popen([
            self.FCEUX_BIN, "-lua", self.LUA_RELAY_PATH, '-loadstate',
            self.SAVE_STATE_PATH, self.ROM_PATH
        ])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 9000))
        s.listen(1)
        conn, addr = s.accept()
        conn.sendall(str(operating_port).encode() + b"\r\n")
        conn.close()
        self.eclient = emulator_bridge('127.0.0.1', operating_port)
        self.frame_interval = frame_interval
        self.joypad = [0, 0, 0, 0, 0, 0, 0]
        self.get_tiles()
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = False

    def get_tiles(self):
        tilebytes =  self.eclient.read_bytes(*locations['tiles'])
        self.tiles = [1 if x > 0 else 0 for x in tilebytes]

    def reset(self):
        self.eclient.load_state(1)
        self.joypad = [0, 0, 0, 0, 0, 0, 0]
        self.get_tiles()
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = False

    def __del__(self):
        self.proc.terminate()

    def update(self):
        self.eclient.joypad_set(self.joypad)
        for x in range(self.frame_interval):
            self.eclient.frame_advance()
        self.get_tiles()
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = self.eclient.read_bytes(*locations['player_state'])[0] == 0x0B

if __name__ == "__main__":
    mario_interface = MarioInterface()
    while True:
        mario_interface.update()
