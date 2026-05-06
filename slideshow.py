#!/home/pi-frame/.virtualenvs/pimoroni/bin/python3

from pathlib import Path
import time
import constants
from PIL import Image
from inky.auto import auto

inky = auto()

def load_image(file):
    try:
        image = Image.open(file)
        resizedimage = image.resize(inky.resolution)
        inky.set_image(resizedimage)
        inky.show()
    except Exception as e:
        print(f"Error loading image {file}: {e}")

total_images = 0
current_image = -1

def get_next_image():
    global current_image
    global total_images
    current_image = current_image + 1

    # need to refresh the image list just in case
    image_list = sorted([
        f
        for f in Path(constants.PHOTOS_DIR).iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg")
    ])
    total_images = len(image_list)

    if total_images == 0:
        current_image = -1
        print("No images found, displaying default image")
        # TODO: I need a default image, haven't decided on one yet
        # load_image("default.jpg")
        return

    if current_image >= total_images:
        current_image = 0
    
    # get current image
    load_image(image_list[current_image])

# Runs forever on a loop
# - Check for lock file
#   - if present, sleep 5 seconds and check again
#   - else:
#     - Load next image from shared folder
#     - Display it on the Inky Impression
#     - Wait 60 seconds
#     - Loop back to next image
#     - If shared folder is empty, display default image

def main_loop():
    while True:
        if Path(constants.LOCK_FILE).exists():
            print("Lock file exists, waiting...")
            time.sleep(5)
        else:
            get_next_image()
            time.sleep(60)

main_loop()