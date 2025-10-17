"""
Globals.py
"""
SoftVers = "17'OCT'25"
"""
───────────────────────────────────────────────────────────────
UNIVERSAL SETTINGS & GLOBAL OBJECT REGISTER

“Everything Everywhere — but kept tidy.”

Acts as the *shared layer* between logic, hardware, and interface.
The goal is **not** to centralise code — but to centralise *clarity*.

Philosophy:
    ▪ HAL owns the hardware
    ▪ Globals gives out the keys
    ▪ Nothing imports each other blindly

    Globals imports HAL (hardware side)
    Logic imports Globals (software side)
    → avoids circular recursion

To-Do::
    ▪ Migrate to config.toml for user-tweakable defaults
    ▪ Add async-safe shared variables (e.g. event flags)
    ▪ Keep imports lazy — microcontrollers dislike fat boots
"""

# ───────────────────────────────────────────────────────────────
# CORE IMPORTS
from machine import Pin, I2C
import uasyncio as asyncio
import utime as time

# ───────────────────────────────────────────────────────────────
# HARDWARE IMPORTS
# These stay lightweight and abstract — *not logic-heavy*
from HardwareLayer import hal

# Display Driver (SSD1306 — I2C)
from lib import ssd1306
# Radio Module (TEA5767 — I2C FM Receiver)
from lib.TEA5767 import Radio


# ───────────────────────────────────────────────────────────────
# I2C BUS INITIALISATION
"""
Define universal I²C bus — both the display and radio ride on this.
Pins are flexible; adjust here for your board variant.
"""
try:
    I2C_SDA = 21
    I2C_SCL = 22
    I2C_FREQ = 400_000  # standard fast-mode
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=I2C_FREQ)
except Exception as e:
    print("Globals :: I2C Init Failed →", e)
    i2c = None


# ───────────────────────────────────────────────────────────────
# DISPLAY HANDLER
"""
The OLED Screen — small but mighty.
If missing, system falls back gracefully.
"""
try:
    screen = ssd1306.SSD1306_I2C(128, 64, i2c)
    screen.fill(0)
    screen.text("Booting...", 20, 30)
    screen.show()
except Exception as e:
    print("Globals :: OLED Init Failed →", e)
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
    radio.set_frequency(100.0)
except Exception as e:
    print("Globals :: Radio Init Failed →", e)
    radio = None


# ───────────────────────────────────────────────────────────────
# CONVENIENCE IMPORTS
"""
Expose common modules & shortcuts.
Avoid importing hardware modules directly from random files.
"""
sleep = time.sleep
Inputs = hal.Inputs
CoarseEncoderStep = hal.CoarseEncoderStep


# ───────────────────────────────────────────────────────────────
# SYSTEM HEARTBEAT / DEBUG
"""
Optional: displays boot diagnostics and versioning info.
Useful for verifying startup chain integrity.
"""
def diagnostics():
    print("─────── SYSTEM DIAGNOSTICS ───────")
    print(f"SoftVers:{SoftVers}")
    print(f"I2C: {i2c}")
    print(f"OLED: {'OK' if screen else 'FAIL'}")
    print(f"Radio: {'OK' if radio else 'FAIL'}")
    print(f"HAL: {hal}")
    print(f"Asyncio: {asyncio}")
    print("──────────────────────────────────")
    if screen:
        screen.fill(0)
        screen.text("Diagnostics", 1, 0)
        screen.text("SoftVers", 1, 8)
        y = 16
        for name, ok in [
            ("SoftVers", SoftVers),
            ("I2C", i2c), 
            ("OLED", screen), 
            ("RADIO", radio)]:
            msg = f"{name}: {'OK' if ok else 'FAIL'}"
            screen.text(msg, 10, y)
            y += 10
        screen.show()


# ───────────────────────────────────────────────────────────────
# ENTRYPOINT — optional self-test
if __name__ == "__main__":
    diagnostics()
