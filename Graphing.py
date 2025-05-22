import machine
import esp32
import framebuf
from machine import Pin, I2C, ADC
import uasyncio as nsync
import utime as time

#===Temperature===
from dht import DHT11
TemHum = DHT11(machine.Pin(19))
#===Voltage===
ADCPin = ADC(Pin(15,))
#==Hall==
#Hall = esp32.raw_temperature() #temp between 100-150, not linear

#===Button===
RedButton = Pin(23, Pin.IN, Pin.PULL_DOWN)
RedLight = Pin(2, Pin.OUT)
Press = 0

#=Readings Bank=
OldVolt=None
OldTemp=None
OldHumi=None

TempF = False

#===Screen===
import ssd1306
i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=1000000)
#fallback; freq=400000
screen = ssd1306.SSD1306_I2C(
    128,
    64,
    i2c,
    60)

#===Indicator Light===
BLUE=Pin(18, Pin.OUT)
BLUE.off()
async def Indicator():
    BLUE.toggle()
    await nsync.sleep(0.00000000001) #very weak blink
    BLUE.toggle()

#===SensorReadings===
async def Sensor_Readings():
    await Indicator()
    global OldTemp, OldHumi, OldVolt
    #make new readings (if possible)
    try:
        #dht11
        TemHum.measure()
        Temp = TemHum.temperature()
        Humi = TemHum.humidity()
        #adc (green wire to red rail)
        val = ADCPin.read_u16()#int between 0-65535
        ADC_Ref = 3.3 #* .90 # assume 10% drop will test later
        Volt = round((val / 65535)*ADC_Ref, 1) # 3.3v max power read
        Volt = min(Volt, ADC_Ref)
        Volt = round(Volt,1)
    except Exception as e:
        print("sensor fail;", e)
        Volt, Temp, Humi = 0, 0, 0  #fallback
    return Volt, Temp, Humi, ADC_Ref

#===Sensor Graph===
async def Sensor_Graph():
    await Indicator()
    global OldTemp, OldHumi, OldVolt, TempF
    Volt, Temp, Humi, ADC_Ref = await Sensor_Readings()# pull most-recent numbers
    
    screen.fill_rect(0,0,128,34,0) # clean above graphs (down to line 34)
    
    #centered title
    title = "//// Max 50'c ////"
    character_width = 8
    title_width = len(title)*character_width #character size
    screen_width = 128
    x_pos = ( screen_width-title_width ) // 2 #title width with equal remainder
    screen.text( title, x_pos, 9, 1) # title, between remainder, at line
    
    #VOLT BOX
    screen.text("VOLT", -1, 16, 1) #slight L-clip is better for spacing
    screen.text("{:.1f}v".format(Volt), -1, 25)
    screen.rect(0, 34, 30, 30, 1)
    percent = (Volt/ADC_Ref)*26
    BarHeight = int(percent)
    screen.fill_rect(2, 36, 26, 26, 0) #box internal space(with 1 dot margin)
    for y in range(26-BarHeight, 26):
        screen.hline(2, 36+y, 26, 1)
    if Volt != OldVolt:
        await Indicator()     
        OldVolt = Volt
    screen.show()

    #TEMP BOX
    screen.text("TEMP", 34, 16, 1)
    screen.rect(35, 34, 30, 30, 1) #OuterLimit(y=34 to 62)
    Farenheit = int(Temp * 9/5 + 32)
    if TempF == True:
        screen.text(str(Farenheit)+"F", 34, 25, 1)
    else:
        screen.text(str(Temp)+"'c", 34, 25, 1)
    
    if Temp != OldTemp:
        await Indicator()
        print("Temp: {}c \n".format(Temp),
              "Temp: {}f \n".format(Farenheit))
        #scroll tempgraph
        await Left_Scroll(screen, 37, 35, 26, 26) #move first
        
        Max_Temp = 50
        #map temp to Y value(62 to 35)
        GraphY = max (36, min(62, 62 - int((Temp/Max_Temp) * 26))) #50 is max
        screen.pixel(62, GraphY, 1)
        #graph floor, temperature in units, devided by graph space
        OldTemp = Temp
        
    #HUMI BOX
    screen.text("HUMI", 69, 16, 1)
    screen.text(str(Humi)+"%", 69, 25, 1)
    screen.rect(70, 34, 30, 30, 1)
    if Humi != OldHumi:
        await Indicator()
        print("Humi: {}%".format(Humi))
        await Left_Scroll(screen, 72, 35, 26, 26)
        Max_Humi = 50 #I'll feel anything over 50
        GraphY = max(32, min(62, 62 - int((Humi/Max_Humi)*26)))
        screen.pixel(97, GraphY, 1)
        OldHumi = Humi

    screen.show()
    await nsync.sleep(1)

async def Left_Scroll(buf, x, y, w, h):
    await Indicator()
    for row in range(y, y + h):
        for col in range(x, x + w - 1):
            #pull from right
            pixel = buf.pixel(col + 1,row)
            buf.pixel(col, row, pixel)
        #clear rightmost
        buf.pixel(x + w - 1, row, 0)
    screen.show()
    await nsync.sleep(0)

def Load_BMP(filename, width, height):
    row_padded = ((width + 31) // 32) * 4
    bytes_per_row = (width + 7) // 8
    raw_buf = bytearray(bytes_per_row * height)

    with open(filename, 'rb') as f:
        f.seek(62)  # adjust if header size differs
        for y in range(height):
            row = f.read(row_padded)
            if len(row) < row_padded:
                break
            # Flip vertically here:
            raw_buf[(height - 1 - y)*bytes_per_row : (height - y)*bytes_per_row] = row[:bytes_per_row]

    return framebuf.FrameBuffer(raw_buf, width, height, framebuf.MONO_HLSB)

async def Intro_Graphic():
    await Indicator()
    x=0
    y=0
    w=50
    h=50
    try:
        bmp = Load_BMP("Matilda.dib", w,h)
        x = 39
        y = 14
        screen.blit(bmp, x,y)
        screen.show()
        await nsync.sleep(0.1)
        screen.fill_rect(x,y, w,h, 0)
    except Exception as e:
        print("failed BMP load: \n", e)

    try:
        bmp = Load_BMP("pixel-art-raven.bmp", w,h)
        x=39
        y=20
        screen.blit(bmp, x,y)
        screen.show()
        await nsync.sleep(0.5)
        screen.fill_rect(x,y, w,h, 0)
    except Exception as e:
        print("failed BMP load: \n", e)

    return
    
async def Main():
    await Indicator()
    await Sensor_Readings() #prep sensor cycle
    await Intro_Graphic() #distraction for prep sensor cycle
    while True:
        await Sensor_Graph()
        await nsync.sleep(5)
        #return #for a one-run debug
nsync.run(Main())
