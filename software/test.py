#!/usr/bin/env python3
import serial
from time import sleep

con = serial.Serial('/dev/ttyUSB0', 38400, timeout=0.1)
mode = 0
r = 0x1ff
g = 0x000
b = 0x000
while True:
    if mode == 0:
        if g < 0x1ff: g += 1
        else: mode = 1
    elif mode == 1:
        if r > 0x000: r -= 1
        else: mode = 2
    elif mode == 2:
        if b < 0x1ff: b += 1
        else: mode = 3
    elif mode == 3:
        if g > 0x000: g -= 1
        else: mode = 4
    elif mode == 4:
        if r < 0x1ff: r += 1
        else: mode = 5
    elif mode == 5:
        if b > 0x00: b -= 1
        else: mode = 0
    con.write(('#S0' + '{:03x}{:03x}{:03x}'.format(r, g, b)).encode())
    sleep(0.0005)
