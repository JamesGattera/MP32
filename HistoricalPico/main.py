#===frivolity===

import os
from machine import *

#===necessary===
import machine
from machine import Pin
import utime as time
import asyncio as sync

#===unnecesary===
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

#bled = Pin("LED", Pin.OUT) # runs from wifi chip

#===outputs===
gled = Pin(1, Pin.OUT)

#===inputs===
Button = 
#===Initial States===
gled.off()



#===working light===
async def indicate():
    gled.on()
    await sync.sleep(0)
    gled.off()

#===main loop===
async def main():
    try:
        while True:
            await indicate()
            await sync.sleep(1)
    except KeyboardInterrupt:
        gled.off()

sync.run(main())

#===IRQ===
