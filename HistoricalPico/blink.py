from machine import *
import utime

pin = Pin("LED", Pin.OUT)
"""
#i2c probe
from machine import Pin, I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
print("I2C devices:", [hex(x) for x in i2c.scan()])
"""
def average_speed():
    timestamps = []
    for i in range(11):
        timestamps.append(utime.ticks_us())  # milliseconds
        utime.sleep_ms(0)  # optional delay
    # Print intervals between readings
    for i in range(1, len(timestamps)):
        delta = utime.ticks_diff(timestamps[i], timestamps[i-1])
        print(f"Interval {i}: {delta} ms")
average_speed()



