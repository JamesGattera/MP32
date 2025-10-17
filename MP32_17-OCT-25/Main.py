"""
Main.py
"""
SoftVers = "17'OCT'25"
"""
───────────────────────────────────────────────────────────────
TOP-LEVEL RUNTIME CONTROL LOOP

Bridges the *Logic Layer* and the *Hardware Abstraction Layer (HAL)*.

The HAL listens to the real world — encoders, buttons, toggles.
This file orchestrates what happens next:
    The Radio sings.
    The Screen smiles.
    The System breathes.

Philosophy:
    HAL listens.
    Main decides.
    Radio sings.
    Screen smiles.

To-Do::
    - Integrate proper async pattern for true non-blocking updates
    - Replace prints with status overlay or event logging (min Nov'25)
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
FM_DEFAULT = 100.0      # startup frequency baseline

# ───────────────────────────────────────────────────────────────
# STATE WRAPPER
class RadioTuner:
    """
    The “Mind” above the HAL’s “Body”.
    Holds all user-visible logic — frequency, encoder position,
    display updates, and radio control.
    """

    def __init__(self):
        # Create encoder instance (using HAL’s internal sub-class)
        self.encoder = hal.Inputs.Encoder(left_pin=14, right_pin=26)
        self.encoder.enable_irq()

        # Local state cache
        self.freq_tenths = int(FM_DEFAULT * 10)
        self.last_pos = self.encoder.read()
        self.freq = FM_DEFAULT

    # ───────────────────────────────────────────────────────────
    def update_frequency(self):
        """
        Reads encoder, applies step size (fine/coarse),
        and pushes the frequency to the radio hardware.
        """
        pos = self.encoder.read()
        if pos == self.last_pos:
            return False  # no change, skip redraws

        delta = pos - self.last_pos
        self.last_pos = pos

        # Coarse / Fine tuning toggle (inherited from HAL global)
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
        Minimal OLED UI.
        Fast, legible, no animation overhead — just information.
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
    Async main coroutine — the heart of the system.
    Keeps the device responsive without wasting cycles.
    """
    print("MAIN :: Init Complete")
    tuner = RadioTuner()

    # Launch HAL’s background watcher (poll-killer / idle manager)
    asyncio.create_task(hal.monitor_inputs())

    # Main operational loop
    while True:
        changed = tuner.update_frequency()
        if changed:
            tuner.draw_display()

        # Soft “screensaver” — sleeps OLED after inactivity
        inactive_ms = time.ticks_diff(time.ticks_ms(), hal._last_activity)
        if inactive_ms > hal._inactivity_limit_ms:
            screen.fill(0)
            screen.text("zZz", 58, 28)
            screen.show()

        await asyncio.sleep_ms(100)


# ───────────────────────────────────────────────────────────────
# ENTRY POINT
"""
Run directly:
    import uasyncio
    uasyncio.run(main())

This pattern guarantees safe coroutine cleanup on soft reboot.
"""
if __name__ == "__main__":
    asyncio.run(main())
