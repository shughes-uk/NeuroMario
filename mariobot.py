import subprocess
import logging
from emulator_bridge import emulator_bridge
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',)

class MarioInterface(object):
    FCEUX_BIN = "../FCEUX/fceux.exe"
    LUA_RELAY_PATH = "hawk_api.lua"
    ROM_PATH = "Super Mario Bros. (JU) (PRG0) [!].nes"
    SAVE_STATE_PATH = "level_1_state.fcs"

    def __init__(self, frame_interval = 5):
        self.proc = subprocess.Popen([self.FCEUX_BIN, "-lua", self.LUA_RELAY_PATH, '-loadstate', self.SAVE_STATE_PATH, self.ROM_PATH])
        self.eclient = emulator_bridge('127.0.0.1', 9000)
        self.frame_interval = 5

    def __del__(self):
        self.proc.terminate()

    def update(self):
        for x in range(self.frame_interval):
            self.eclient.frame_advance()

mi = MarioInterface()
while True:
    mi.update()
