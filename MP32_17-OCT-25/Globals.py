"""
Globals.py
"""
SoftVers = "17'OCT'25"
"""
───────────────────────────────────────────────────────────────
"UNIVERSAL SETTINGS & GLOBAL OBJECTS"
 - "Everything Everywhere"
 - "Mise En Place"

Shared layer between logic, hardware, and interface
The goal is centralise a cheatsheet/reference

Philosophy:
    - HAL covers hardware
    - Globals covers convenience
    - Main covers both
    Globals imports HAL (hardware)
    Logic imports Globals (software)
        *******avoids circular recursion
To-Do::
    - investigate rumoured "config.toml" tweakable defaults
    - add async-safe variables/flags/debug messages
    - keep imports light - apparently "microcontrollers dislike fat boots"
"""
# ───────────────────────────────────────────────────────────────
# CORE IMPORTS
from machine import Pin, I2C
import uasyncio as asyncio
import utime as time
# ───────────────────────────────────────────────────────────────
# HARDWARE IMPORTS
# Stay lightweight and abstract, *not logic-heavy*
from HardwareLayer import hal
# Display Driver (SSD1306 — I2C)
from lib import ssd1306
# Radio Module (TEA5767 — I2C FM Receiver)
from lib.TEA5767 import Radio
#
asyncio.sleep_ms(10)
# ───────────────────────────────────────────────────────────────
# I2C BUS INITIALISATION
"""
Define universal I2C bus
    both the display and radio ride on this
    (all I2C in future)
I/O pins are flexible;
    adjust here for board variant
"""
try:
    I2C_SDA = 21
    I2C_SCL = 22
    I2C_FREQ = 400_000  # underscore is comma
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)
    asyncio.sleep_ms(10)
except Exception as e:
    print("Globals :: I2C Fail e>", e)
    i2c = None
# ───────────────────────────────────────────────────────────────
# DISPLAY HANDLER
"""
OLED Screen
If missing, system prints E.
"""
try:
    screen = ssd1306.SSD1306_I2C(128, 64, i2c)
    screen.fill(0)
    screen.text("Display Booting...", 0, 0)
    print(		"Display Booting...")
    screen.show()
    asyncio.sleep_ms(10)
except Exception as e:
    print("Globals :: OLED Init Failed e>", e)
    screen = None
# ───────────────────────────────────────────────────────────────
# RADIO DRIVER
"""
FM Radio via TEA5767
    - Connected via I²C (same bus)
    - Controlled via Radio.set_frequency(float MHz)
"""
try:
    radio = Radio(i2c)
    asyncio.sleep_ms(10)
    try:
        radio.set_frequency(100.0)
    except Exception as e:
        print("Globals :: Radio Freq Fail e>", e)
    try:
        screen.text("Radio Booting...", 0, 8)
        print(		"Radio Booting...")
        screen.show()
    except Exception as e:
        print("Radio :: No Screen")
except Exception as e:
    print("Globals :: Radio Init Failed e>", e)
    radio = None
asyncio.sleep_ms(10)
# ───────────────────────────────────────────────────────────────
# CONVENIENCE IMPORTS
"""
Exposes common modules & shortcuts
Avoids importing hardware modules directly from random files
"""
sleep = time.sleep
Inputs = hal.Inputs
CoarseEncoderStep = hal.CoarseEncoderStep
# ───────────────────────────────────────────────────────────────
# SYSTEM HEALTH / DEBUG
"""
Optional, display boot diagnostics and versioning info
For verifying startup chain integrity
Could be fun for a Pip-Boy-Style startup
"""
async def diagnostics(Holdopen = 1, summary = False): # 1-second default for debug
    print("─────── SYSTEM DIAGNOSTICS ───────")
    print(f"SoftVers:	{SoftVers}")
    print(f"I2C: 		{i2c}")
    print(f"OLED: 		{'OK' if screen else 'FAIL'}")
    print(f"Radio: 		{'OK' if radio else 'FAIL'}")
    print(f"HAL: 		{hal}")
    print(f"Asyncio: 	{asyncio}")
    print("──────────────────────────────────")
    if screen:
        screen.fill(0)
        screen.text("Diagnostics", 1, 0)
        screen.text(f"Soft.V {SoftVers}", 1, 9)
        y = 18
        for name, ok in [
            ("HAL  ", hal),
            ("I2C  ", i2c), 
            ("OLED ", screen), 
            ("RADIO", radio)
            ]:
            msg = f"{name} : {'OK' if ok else 'FAIL'}"
            screen.text(msg, 0, y)
            y += 8 # smallest reasonable        
        screen.show()
        
        # :: Creative Lisence ::
        # numerical hold-open count-down
        # three-digit, bottom right corner
        cornerX 	= 106 #106
        cornerY 	= 57 #57
        for X in range(Holdopen, 0, -1):
            screen.text(str(X), 105, 57) # 105, 57
            Holdopen -= 1
            print(str(X))
            screen.show()
            await asyncio.sleep(1.5)
            #clears old digits (T-Left, B-Right, B-Left, B-Right, Colour)
            screen.fill_rect(cornerX, cornerY, 24, 8, 0)
            
        screen.fill(0)
        screen.show()
        await asyncio.sleep_ms(10)
# ───────────────────────────────────────────────────────────────
# ENTRYPOINT — optional self-test
if __name__ == "__main__":
    try:
        asyncio.run(diagnostics())
    except Exception as e:
        print("Diagnostics error:", e)
