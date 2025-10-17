"""
boot.py
"""
SoftVers = "17'OCT'25"
"""
───────────────────────────────────────────────────────────────
SYSTEM ENTRYPOINT - FIRST BREATH

MicroPython automatically executes this file after reset
The “spark” before the Main.py runtime

Philosophy:
    Keep it Light - boot.py should prepare, not perform.

Roles:
    - Initialise Globals (hardware + interfaces)
    - Run a brief startup animation (BootScreenIndicator)
    - Hand off control to Main.py (core logic)

If something breaks here - nothing else boots.
"""
# ───────────────────────────────────────────────────────────────
# CORE IMPORTS
import sys
import Globals
import uasyncio as asyncio
# ───────────────────────────────────────────────────────────────
# OPTIONAL VISUAL STARTUP (Boot Art)
"""
BootScreenIndicator — tiny OLED animation.
Gives the illusion of “boot time” while hardware settles.
I like that:
    Art at the start.
"""
try:
    import BootScreenIndicator as BSI
    if hasattr(BSI, "run_animation"):
        BSI.run_animation()
    else:
        print("BSI :: no run_animation() found, skipping")
except Exception as e:
    print("BSI :: skipped →", e)

# ───────────────────────────────────────────────────────────────
# MAIN PROGRAM HANDOFF
"""
Final handoff — execution continues into Main.py.
If Globals or BootScreen fail, Main will *still* attempt to run.
Allows future “headless” recovery or debugging.
"""
try:
    import Main
    asyncio.run(Main.main())
    # Reload in case of soft reboot or cached copy
    sys.modules.pop("Main", None)
    import Main
except:
    print("Boot.py :: NoMain")