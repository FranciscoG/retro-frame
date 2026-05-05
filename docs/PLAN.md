# Plan

## Hardware

- Raspberry Pi Zero WH running `Raspbian GNU/Linux 13 (trixie, debian 13.4)`
- Pimoroni Inky Impression 7.3" display (HAT, connects via GPIO)
- USB floppy drive enclosure
- Power supply

**Shared folder** — `/home/pi/photos/` as the communication channel between the two daemons

**Lock file** — `/tmp/floppy.lock` to pause the slideshow during disk loading

## Software

- Python
- https://github.com/pimoroni/inky

## Daemon 1 — Floppy Loader

- Sits idle, doing nothing, making no noise
- Triggered by a button press (Button A on the Inky Impression)
- On button press:
  - Create lock file
  - Mount the floppy disk
  - Delete old images from shared folder
  - Copy new images (jpeg/png/tiff, whatever image files the Sony Mavica FD supports) from floppy to shared folder
  - Unmount the floppy
  - Delete lock file

## Daemon 2 — Slideshow

- Runs forever on a loop
- Check for lock file
  - if present, sleep 5 seconds and check again
  - else:
    - Load next image from shared folder
    - Display it on the Inky Impression
    - Wait 60 seconds
    - Loop back to next image
    - If shared folder is empty, display default image

## Display states

**Default image** — shown when shared folder is empty
**Loading screen** — static image shown while lock file is present
**Slideshow** — cycles through all images in shared folder, 60 seconds per image

## Buttons

The Inky e-ink screen has 4 buttons on it. We'll use 2 of them:

- **Button A** — trigger floppy load
- **Button B** — skip to next image manually
