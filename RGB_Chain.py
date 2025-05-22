#RGB CHAIN#

import machine
from machine import Pin, ADC
import utime as time
import uasyncio as nsync


#=define output
Red = Pin(23, Pin.OUT)
Green = Pin(22, Pin.OUT)
Blue = Pin(23, Pin.OUT)
Pins = (Red,) #Green, #Blue

#=define input=
Button = Pin(2, Pin.IN)
RedButton = Button

#=define output=
async def test():
    for led in Pins:
        led.value(1)
        await nsync.sleep(.1)
        led.value(0)
i=0
#while i = :
nsync.run(test())