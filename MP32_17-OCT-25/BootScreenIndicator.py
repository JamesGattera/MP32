"""
"BootScreenIndicator.py"
"""
SoftVers = "17'OCT'25"
"""
Displays a false loading indicator
Offers system some time to load
I like how it looks, I like "art on start"
"""
import Globals
I2C = Globals.I2C
Pin = Globals.Pin
ssd1306 = Globals.ssd1306
time = Globals.time



# I2C setup
Screen_i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# Screen object
screen = ssd1306.SSD1306_I2C(128, 64, Screen_i2c)

def run_animation():

    #Boot progress bar(height of yellow band)
    screen.text("Booting...",0,20)
    for i in range(0, 128, 130):
        screen.fill_rect(0, 0, i, 16, 1)
        screen.show()
        time.sleep(0.1)
    screen.fill(0)
    screen.show()

    "The Ready Blink"
    screen.text("Ready", 38, 28)
    screen.show()
    time.sleep(0.01)
    screen.fill(0)
    screen.show()
