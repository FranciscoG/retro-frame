
from pathlib import Path

PHOTOS_DIR = str(Path.home() / "photos")
CONFIG_PATH = str(Path.home() / ".retro-frame.conf")
LOCK_FILE = "/tmp/floppy.lock"
USB_DEVICE = "/dev/sda"
DEFAULT_INTERVAL = 1800 # 30 minutes