#!/home/pi-frame/.virtualenvs/pimoroni/bin/python3

from pathlib import Path
import time
from tkinter import font
from turtle import right
import constants
import utils
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from inky.auto import auto

inky = auto()
default_image_shown = False

# print([a for a in dir(inky) if a.isupper()])
# ['BLACK', 'BLUE', 'DESATURATED_PALETTE', 'GREEN', 'HEIGHT', 'RED', 'SATURATED_PALETTE', 'WHITE', 'WIDTH', 'YELLOW']

def draw_default_image():
    global default_image_shown
    if default_image_shown:
        return

    width, height = inky.resolution
    image = Image.new("P", (width, height), inky.BLACK)
    draw = ImageDraw.Draw(image)

    horizon_y = int(height * 0.55)

    sun_radius = int(height * 0.30)
    sun_cx = width // 2
    sun_cy = horizon_y - int(sun_radius * 0.4)
    draw.ellipse(
        (
            sun_cx - sun_radius,
            sun_cy - sun_radius,
            sun_cx + sun_radius,
            sun_cy + sun_radius,
        ),
        fill=inky.YELLOW,
    )

    # Carve horizontal bars out of the sun's lower half (the synthwave look)
    bar_count = 6
    for i in range(bar_count):
        bar_y = sun_cy + int((i / bar_count) * sun_radius * 0.95)
        bar_thickness = 3 + i * 2
        draw.rectangle(
            (sun_cx - sun_radius, bar_y, sun_cx + sun_radius, bar_y + bar_thickness),
            fill=inky.BLACK,
        )

    # Wipe everything below the horizon so the sun's lower edge doesn't bleed into the grid
    draw.rectangle((0, horizon_y, width, height), fill=inky.BLACK)

    # Vertical grid lines fan out from a narrow band on the horizon to the full bottom width
    vertical_count = 17
    top_band = int(width * 0.35)
    bottom_band = int(width * 1.4)
    top_left = (width - top_band) // 2
    bottom_left = (width - bottom_band) // 2
    for i in range(vertical_count):
        t = i / (vertical_count - 1)
        top_x = top_left + int(t * top_band)
        bottom_x = bottom_left + int(t * bottom_band)
        draw.line((top_x, horizon_y, bottom_x, height), fill=inky.RED, width=1)

    # Horizontal grid lines, spaced by a power curve so they tighten near the horizon
    horizontal_count = 8
    for i in range(1, horizontal_count + 1):
        t = (i / horizontal_count) ** 2
        y = horizon_y + int(t * (height - horizon_y))
        draw.line((0, y, width, y), fill=inky.RED, width=1)

    # Bright horizon line on top of everything
    draw.line((0, horizon_y, width, horizon_y), fill=inky.WHITE, width=2)

    inky.set_image(image)
    inky.show()
    default_image_shown = True


def draw_loading():
    # Create new PIL image with a white background
    image = Image.new("P", (inky.width, inky.height), inky.WHITE)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FredokaOne, 72)

    # draw some text
    text = "Loading..."
    draw.text(
        (inky.width // 2, inky.height // 2),
        text,
        inky.BLACK,
        font,
        anchor="mm",
    )
    inky.set_image(image)
    inky.show()


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
        draw_default_image()
        return

    global default_image_shown
    default_image_shown = False

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
    loading_image_displayed = False
    while True:
        if Path(constants.LOCK_FILE).exists():
            print("Lock file exists, waiting...")
            if not loading_image_displayed:
                draw_loading()
                loading_image_displayed = True
            time.sleep(5)
        else:
            get_next_image()
            loading_image_displayed = False
            time.sleep(60)


def start_slideshow():
    main_loop()
