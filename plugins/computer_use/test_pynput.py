import time
from pynput.keyboard import Controller, Key
import platform

kb = Controller()
time.sleep(2)
with kb.pressed(Key.cmd):
    kb.tap('f')
print("Pressed cmd+f")
