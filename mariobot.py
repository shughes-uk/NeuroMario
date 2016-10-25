import subprocess
import logging
from emulator_bridge import emulator_bridge
from mariolocs import locations

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s: %(message)s', )


class MarioInterface(object):
    FCEUX_BIN = "../FCEUX/fceux.exe"
    LUA_RELAY_PATH = "hawk_api.lua"
    ROM_PATH = "Super Mario Bros. (JU) (PRG0) [!].nes"
    SAVE_STATE_PATH = "level_1_state.fcs"

    def __init__(self, frame_interval=5):
        self.proc = subprocess.Popen([
            self.FCEUX_BIN, "-lua", self.LUA_RELAY_PATH, '-loadstate',
            self.SAVE_STATE_PATH, self.ROM_PATH
        ])
        self.eclient = emulator_bridge('127.0.0.1', 9000)
        self.frame_interval = 2
        self.joypad = [0, 0, 0, 0, 0, 0, 0]
        self.tiles = self.eclient.read_bytes(locations['tiles'][0],
                                             locations['tiles'][1])
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = False

    def reset(self):
        self.eclient.load_state(1)
        self.joypad = [0, 0, 0, 0, 0, 0, 0]
        self.tiles = self.eclient.read_bytes(locations['tiles'][0],
                                             locations['tiles'][1])
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = False

    def __del__(self):
        self.proc.terminate()

    def update(self):
        self.eclient.joypad_set(self.joypad)
        for x in range(self.frame_interval):
            self.eclient.frame_advance()
        self.eclient.read_bytes(locations['tiles'][0], locations['tiles'][1])
        self.mariox = self.eclient.read_bytes(0x6D, 1)[0] * 0x100 + self.eclient.read_bytes(0x86, 1)[0]
        self.mario_dead = self.eclient.read_bytes(*locations['player_state'])[0] == 0x0B

if __name__ == "__main__":
    mario_interface = MarioInterface()
    while True:
        mario_interface.update()
