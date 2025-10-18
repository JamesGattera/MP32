"""
HardwareLayer.py
"""
SoftVers = "17'OCT'25"
"""
Linebreak for copying lower;;

# ───────────────────────────────────────────────────────────────
STANDALONE HARDWARE ABSTRACTION LAYER (HAL)
    This file to gather all physical 'touchpoints'
    Buttons, encoders, toggles - the physical human-machine bridge.

No dependency on .Globals - HAL is a STANDALONE MOD
    (to avoid recursion)
    
"Logic lives above; electrons buzz below"
    This file lives in the in-between, 
    translating mechanical clicks

All editorial choices, layout, comments, tinkering, testing, and style choices are credit to me; 
    James :D
#
    To-Do :: Remove/clean all prints when certain (min Nov'25)
    To-Do :: Relearn *Args & **Kwargs
    To-Do :: Adaptive/Adaptable Timeout Timer
#        
        REMINDER :: IRQ handlers MUST be SMALL & LIGHT
            No Prints, No internal Functions
            RInstead;; Reference and signal external fuinctions
"""

# IMPORTS
from machine import Pin, I2C
import utime as time
import uasyncio as asyncio
# DONT IMPORT .PY

# ───────────────────────────────────────────────────────────────
# HAL CORE
"""
HAL; Unified Hardware Box.
Container for all human inputs.
Abstracts;
    bouncing, 
    click-clack, 
    signal spikes
Returns;
    clean, logical events 
    for the UI 
    and application.
"""
class HAL:

    def __init__(self):        
        
        # ───────────────────────────────────────────────────────
        # Coarse/Fine toggle state
        # False = Fine
        # True = Coarse
        # Default is fine; the button flips it, IRQ style.
        self._coarse_toggle_pending = False
        self.CoarseEncoderStep = False

        # ───────────────────────────────────────────────────────
        # Structured namespace for all input devices
        # Holds buttons, encoders, and any future sensors
        self.Inputs = self.InputDevices(self)

        # ───────────────────────────────────────────────────────
        #Async Queue for hardware events
        #	Any event that happens (button, encoder, toggle),
        #	is pushed here to get handled by upper layers.
        #
        #Asyncio Helper :: stubby fallback for missing Queue
        #(Safe For MicroPython.uasyncio as asyncio)
        try:
            self._update_queue = asyncio.Queue()
        except AttributeError:
            class _StubQueue:
                def __init__(self):
                    self._q = []
                async def put(self, item):
                    self._q.append(item)
                async def get(self):
                    if not self._q:
                        return None
                    return self._q.pop(0)
                def put_nowait(self, item):
                    "Synchronous append; safe for IRQ context."
                    self._q.append(item)
                def empty(self):
                    return len(self._q) == 0
            self._update_queue = _StubQueue()



        # ───────────────────────────────────────────────────────
        #Timeout-Timer for Poll Killer
        #Stops active polling(wasteful) if no input after a while(tunable)
        self._last_activity = time.ticks_ms()
        self._polling_active = True
        self._poll_sleep_ms = 200
        self._inactivity_limit_ms = 5000  # >5 seconds: end polling / go idle
    
    ##yet another irq handler/wrapper ::
    def ToggleCoarse(self, pin=None):
        "Called directly by encoder button IRQ"
        self._coarse_toggle_pending = True
        self.mark_activity()
    # ───────────────────────────────────────────────────────────────
    # Poll Killer / Activity Tracker
    def mark_activity(self):
        """
        Notes input signal 
        Resets Timeout Timer
        Wakes HAL from idle cycle if asleep
        Call this from any input;;
            hal.mark_activity()
        """
        self._last_activity = time.ticks_ms()
        if not self._polling_active:
            #print("Poll Killer :: HAL Waking Poll Killer")
            self._polling_active = True

    # ───────────────────────────────────────────────────────────────
    # Minimal Polling / Watchdog Task
    async def monitor_inputs(self):
        """
        Async background watcher task

        Event-driven first, polling second.
        Polling is extremely lightweight,
            only wakes when active
            or after long inactivity
            to catch missed events

        Call from main loop:
            asyncio.create_task(hal.monitor_inputs())

        Roles:
            - Detect 'edge events' not caught by IRQs
            - Debounce slow mechanical buttons
            - Feed updates into upper layers
            - Poll Killer: kills polling when idle
        """
        #print("Poll Killer :: Starting Monitor")
        while True:
            if self._polling_active:
                if self._coarse_toggle_pending:
                    self.CoarseEncoderStep = not self.CoarseEncoderStep
                    await self._update_queue.put(("CoarseToggle",
                                                  self.CoarseEncoderStep))
                    self._coarse_toggle_pending = False
                
                # print("Poll Killer :: Heart UP", self._polling_active) #Debug, DROWNS REPL
                
                # Idle Timeout Comparator
                if time.ticks_diff(time.ticks_ms(),
                                   self._last_activity) > self._inactivity_limit_ms:
                    #print("Poll Killer :: Killing Polls")
                    self._polling_active = False

            else:
                # Heartbeat / debug placeholder when idle
                #print("Poll Killer :: Heart DOWN", self._polling_active) #Debug, DROWNS REPL
                
                # Sleep longer to save cycles while idle
                await asyncio.sleep_ms(self._poll_sleep_ms)

            #TaskStarvationStopper ::
            await asyncio.sleep_ms(50)
 
            # Placeholder for future sensor expansion
            # e.g. self.Inputs.ExtraButton.was_pressed()
            # e.g. forward encoder delta to UI

    # ───────────────────────────────────────────────────────────────
    # Async helper to consume hardware events
    async def next_event(self):
        """
        Wait for the next hardware event (button press, toggle, encoder)
        Returns a tuple: (event_name, value)
        """
        return await self._update_queue.get()

    # ───────────────────────────────────────────────────────────────
    # INPUT DEVICES COLLECTION
    # Encapsulates buttons, encoders, etc., into a neat namespace
    class InputDevices:
        def __init__(self, hal):
            self.hal = hal
            
            # Encoder Rotation Pins ::
            self.EncoderPins = self.Encoder(left_pin=14, right_pin=26)
            self.EncoderPins.enable_irq() #already stated in .Encoder

            # Encoder push-button: toggles Coarse/Fine
            self.EncoderButton = self.Button(pin=27, pull=Pin.PULL_UP)
            self.EncoderButton.pin.irq(
                trigger=Pin.IRQ_FALLING,
                handler=self.hal.ToggleCoarse
            )
        # ───────────────────────────────────────────────────────────────
        class Button:
            """
            Simple digital button with edge detection logic.
            No software debounce; mechanical edges detected via state machine.
            """
            def __init__(self, pin, pull=Pin.PULL_UP):
                self.pin = Pin(pin, Pin.IN, pull)
                self.last_state = self.pin.value()

            def is_pressed(self):
                """Returns True while button is held down"""
                return self.pin.value() == 0

            def was_pressed(self):
                """
                Returns True once per press event.
                Resets after release.
                """
                state = self.pin.value()
                if state == 0 and self.last_state == 1:
                    self.last_state = 0
                    return True
                elif state == 1:
                    self.last_state = 1
                return False

        # ───────────────────────────────────────────────────────────────
        class Encoder:
            """
            Rotary encoder FSM: converts mechanical phase shifts into clean steps.
            Software debounce not needed: FSM is the filter.
            Can be IRQ-driven for minimal polling.
            """
            def __init__(self, left_pin, right_pin):
                self.left = Pin(left_pin, Pin.IN, Pin.PULL_UP)
                self.right = Pin(right_pin, Pin.IN, Pin.PULL_UP)
                self.position = 0
                self.state = 0
                self.irq_enabled = False

            def read_pins(self):
                return self.left.value(), self.right.value()

            def update(self, pin=None):
                """FSM update; returns True if position changed"""
                clk, dt = self.read_pins()
                changed = False

                # Idle / starting state
                if self.state == 0:
                    if clk == 0:
                        self.state = 1
                    elif dt == 0:
                        self.state = 4

                # Clockwise rotation
                elif self.state in [1, 2, 3]:
                    if self.state == 1 and dt == 0:
                        self.state = 2
                    elif self.state == 2 and clk == 1:
                        self.state = 3
                    elif self.state == 3 and clk == 1 and dt == 1:
                        self.state = 0
                        self.position += 1
                        changed = True

                # Counter-clockwise rotation
                elif self.state in [4, 5, 6]:
                    if self.state == 4 and clk == 0:
                        self.state = 5
                    elif self.state == 5 and dt == 1:
                        self.state = 6
                    elif self.state == 6 and clk == 1 and dt == 1:
                        self.state = 0
                        self.position -= 1
                        changed = True

                return changed
            
            def irq_handler(self, pin):
                """
                Safe wrapper for MicroPython Pin.irq #cant read 'Bool=None'
                """
                changed = self.update()   # run FSM
                """
                AI SUGGESTED OPTINALS ::
                # Optionally push to HAL queue here if needed:
                # hal._update_queue.put_nowait(("Encoder", self.position))
                """

            def enable_irq(self):
                """
                Attach FSM update to pins.
                Hardware calls update() on any edge change.
                IRQ handlers must remain small & light.
                """
                if self.irq_enabled:
                    return
                self.left.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                              handler=self.irq_handler)
                self.right.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                               handler=self.irq_handler)
                self.irq_enabled = True

            def read(self):
                """Current absolute encoder position"""
                return self.position


# ───────────────────────────────────────────────────────────────
# GLOBAL HAL INSTANCE
# All system modules can import and use ;;
#     from HardwareLayer import hal
hal = HAL()

