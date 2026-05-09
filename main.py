#!/home/pi-frame/.virtualenvs/pimoroni/bin/python3

import buttons
import slideshow
import threading
import subprocess
import constants
from pathlib import Path


def spawnFloppyDiskLoader():
    if Path(constants.LOCK_FILE).exists():
        print(
            "Lock file exists, skipping button press to avoid conflict with slideshow"
        )
        return

    print("Button A pressed, launching floppy loader")
    floppy_loader_path = Path(__file__).parent / "floppy_loader.py"
    subprocess.Popen([str(floppy_loader_path)], start_new_session=True)


def onButtonPress(label):
    print(f"Button {label} was pressed!")
    if label == "A":
        spawnFloppyDiskLoader()


# Start the button listener in a separate thread so it doesn't block the slideshow
threading.Thread(target=buttons.begin, args=(onButtonPress,), daemon=True).start()

try:
    print("Starting slideshow...")
    slideshow.start_slideshow()
except KeyboardInterrupt:
    print("Exiting...")
