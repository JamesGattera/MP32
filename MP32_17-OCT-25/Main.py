"""
Main.py
"""
SoftVers = "17'OCT'25"
"""
───────────────────────────────────────────────────────────────
"TOP-LEVEL RUNTIME CONTROL LOOP"

Bridges the 'LogicLayer' and the 'HardwareLayer.py'; HAL

Design Pattern ::
    boot.py					#Boot
    BootScreenIndicator.py	#Video
    Main.py 				#Runtime
    HardwareLayer.py 		#Inputs
    Radio.py				#Audio

To-Do::
    - Integrate async pattern for more non-blocking
    - Replace prints(min(Nov'25))
    - Etymology of Boolean
"""

# ───────────────────────────────────────────────────────────────
# IMPORTS
import uasyncio as asyncio
import utime as time

# Internal modules
from HardwareLayer import hal
from Globals import screen, radio, sleep

# ───────────────────────────────────────────────────────────────
# CONSTANTS / LIMITS
FM_MIN_TENTHS = 875     # 87.5 MHz lower clamp
FM_MAX_TENTHS = 1080    # 108.0 MHz upper clamp
FM_DEFAULT = 100.0      # startup frequency

# ───────────────────────────────────────────────────────────────
# STATE WRAPPER
class RadioTuner:
    """
    Holds user-visible logic:
        frequency,
        encoder position,
    
        display updates
        radio control.
    """
    def __init__(self):
        # Create encoder instance (using HAL .sub-class)
        self.encoder = hal.Inputs.EncoderPins
        self.encoder.enable_irq()
        # Local state caches
        self.freq_tenths = int(FM_DEFAULT * 10)
        self.last_pos = self.encoder.read()
        self.freq = FM_DEFAULT
        
    # ───────────────────────────────────────────────────────────
    def update_frequency(self):
        """
        Reads encoder,
        Applies step size (Fine/Coarse)
        Pushes frequency to radio hardware
        """
        pos = self.encoder.read()
        if pos == self.last_pos:
            return False  # no change; skip redraw
        delta = pos - self.last_pos #delta=change in val
        self.last_pos = pos
        # Coarse / Fine tuning toggle from .HAL
        step = 10 if hal.CoarseEncoderStep else 1
        self.freq_tenths += delta * step
        # Clamp to FM range
        self.freq_tenths = max(FM_MIN_TENTHS, min(FM_MAX_TENTHS, self.freq_tenths))
        self.freq = self.freq_tenths / 10.0
        # Push to radio hardware
        radio.set_frequency(self.freq)
        # Keep the “Poll Killer” awake
        hal.mark_activity()
        return True

    # ───────────────────────────────────────────────────────────
    def draw_display(self):
        """
        OLED UI.
        """
        screen.fill(0)
        screen.text(f"FM: {self.freq:.1f}", 30, 30)
        mode = "Coarse" if hal.CoarseEncoderStep else "Fine"
        screen.text(f"Mode: {mode}", 0, 0)
        screen.show()
# ───────────────────────────────────────────────────────────────
# CORE RUNTIME
async def main():
    """
    Async main 'co'routine - min(cycles
    """
    print("MAIN :: Init Complete")
    tuner = RadioTuner()
    #Launch HAL watcher (Poll Killer//idle manager)
    asyncio.create_task(hal.monitor_inputs())
    #Main operation loop
    while True:
        """Display Triggers ::"""
        redraw = False #defined display value
        #Drain Event Queue;;
        while not hal._update_queue.empty():
            event, value = await hal.next_event()
            if event == "CoarseToggle":
                redraw = True
        #Check For Encoder Change;;
        if tuner.update_frequency():
            redraw = True
        #if Redraw boolean = 'True' ANYWHERE
        if redraw:
            tuner.draw_display()
        """ScreenSaver :: sleeps OLED after inactivity"""
        inactive_ms = time.ticks_diff(time.ticks_ms(), hal._last_activity)
        if inactive_ms > hal._inactivity_limit_ms:
            for _ in range(2):
                screen.fill(0)
                screen.text("z", 121,56)
                screen.show()
                await asyncio.sleep_ms(1100)
                "stylistic blink"
                screen.fill(0)
                screen.show()
                await asyncio.sleep_ms(900)
        await asyncio.sleep_ms(100)
# ───────────────────────────────────────────────────────────────
# ENTRY POINT
"""
Run directly:
    import uasyncio
    uasyncio.run(main())

semi-safe reboot
"""
if __name__ == "__main__":
    asyncio.run(main())
