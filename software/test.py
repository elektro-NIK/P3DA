#!/usr/bin/env python3
import serial
from time import sleep


def gamma(x): return round((x / 255) ** 2.8 * 511)


con = serial.Serial('/dev/ttyUSB0', 38400, timeout=0.1)
mode = 0
r = 0x1ff
g = 0x000
b = 0x000

while True:
    if mode == 0 and g < 0xff:
        g += 1
    elif mode == 1 and r > 0x00:
        r -= 1
    elif mode == 2 and b < 0xff:
        b += 1
    elif mode == 3 and g > 0x00:
        g -= 1
    elif mode == 4 and r < 0xff:
        r += 1
    elif mode == 5 and b > 0x00:
        b -= 1
    elif mode != 5:
        mode += 1
    else:
        mode = 0
    con.write(('#S0' + '{:03x}{:03x}{:03x}'.format(gamma(r), gamma(g), gamma(b))).encode())
    sleep(0.0005)
