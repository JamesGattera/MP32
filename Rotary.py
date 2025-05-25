import machine
import esp32
import framebuf
from machine import Pin, I2C, ADC, disable_irq, enable_irq
import uasyncio as nsync
import utime as time

#===Screen===
import ssd1306
i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=400000)
#fallback; freq=400000
screen = ssd1306.SSD1306_I2C(
    128,
    64,
    i2c,
    60)

#Rotary Encoder Testcode
CLK = Pin(19, Pin.IN, Pin.PULL_UP,)
DT = Pin(23, Pin.IN, Pin.PULL_UP,)

#Values Bank
Debounce_ms = 3 #biggest issue rn
LastClock = 0
Position = 0 #location of turns, relative to boot-up
Updated = False #indicator for main loop


#Relearn Button IRQs...
def Rotate(pin):
    global Position, Updated, LastClock
    
    Now = time.ticks_ms()
    
    if time.ticks_diff(Now, LastClock)>Debounce_ms:
        if DT.value(): #if it has any value
            Position +=1
            #print("+1")
        else:
            Position -=1
            #print("-1")
        Updated = True #Set indicator for main loop
        LastClock = Now #Update for Debounce 

CLK.irq(trigger=CLK.IRQ_FALLING, handler=Rotate, ) #now using as trigger, not comparator
#DT.irq(trigger=B.IRQ_FALLING, handler=Rotating, ) #now using as indicator, not comparator



async def main():
    global Updated
    
    while True:
        if Updated:
            screen.fill(1) #Lights on

            # Copying position outside IRQ
            state = disable_irq() #disable inputs for screen conflict
            pos = Position #pull data 'safely'
            Updated = False #reset interrupt trigger
            enable_irq(state) #re-enable inputs
            

            screen.text("Position: {}".format(pos),0,0,0)
            screen.pixel(64,32,0) #Center Mark
            screen.show() ##LTBL
            
        await nsync.sleep_ms(10) #debounce, and time for show.

nsync.run(main())
