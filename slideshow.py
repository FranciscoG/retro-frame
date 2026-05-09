#!/home/pi-frame/.virtualenvs/pimoroni/bin/python3

from pathlib import Path
import time
import constants
import utils
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from inky.auto import auto

inky = auto()


def default_image():
    inky_display = auto()

    # Create new PIL image with a white background
    image = Image.new(
        "P", (inky_display.width, inky_display.height), inky_display.WHITE
    )
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FredokaOne, 72)

    # draw some shapes
    draw.rectangle((50, 50, 200, 200), fill=inky_display.YELLOW)  # Rectangle
    draw.ellipse((150, 150, 300, 300), fill=inky_display.RED)  # Circle (ellipse)
    draw.line((0, 0, 400, 400), fill=inky_display.BLUE, width=10)  # Diagonal line

    # draw some text
    draw.text((0, 0), "Retro Frame", inky_display.BLACK, font)

    inky_display.set_image(image)
    inky_display.show()


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
    image_list = sorted(
        utils.get_files_with_extensions(constants.PHOTOS_DIR, (".jpg", ".jpeg"))
    )
    total_images = len(image_list)

    if total_images == 0:
        current_image = -1
        print("No images found, displaying default image")
        default_image()
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


def start_slideshow():
    main_loop()
