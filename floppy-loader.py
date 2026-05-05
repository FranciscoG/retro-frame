#!/home/pi-frame/.virtualenvs/pimoroni/bin/python3

import os
import shutil
import subprocess
import glob
from pathlib import Path
import time
import buttons
import constants

if not os.path.exists(constants.PHOTOS_DIR):
    os.makedirs(constants.PHOTOS_DIR)


def mount_usb_floppy(device=constants.USB_DEVICE):
    try:
        # udisksctl mount -b /dev/sda
        result = subprocess.run(
            ["udisksctl", "mount", "-b", device],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Mounted successfully: {result.stdout}")
        MOUNT_DIR = result.stdout.split(" ")[-1].strip()
        print(f"Mount directory: {MOUNT_DIR}")
        return MOUNT_DIR
    except subprocess.CalledProcessError as e:
        print(f"Error mounting: {e.stderr}")
        return None


def unmount_usb_floppy(device=constants.USB_DEVICE):
    try:
        # udisksctl unmount -b /dev/sda
        result = subprocess.run(
            ["udisksctl", "unmount", "-b", device],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Unmounted successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error unmounting: {e.stderr}")


def delete_old_images():
    try:
        filesList = glob.glob(constants.PHOTOS_DIR + "/*")
        for file in filesList:
            print("Removing File {}".format(file))
            os.remove(file)
        print("All Files are Remove if Existed")
        return True
    except Exception as e:
        print(f"Error deleting old images: {e}")
        return False


def copy_new_images(source, destination=constants.PHOTOS_DIR):
    try:
        # mavica saves images to the root of the floppy, all as jpeg
        files = [f for f in Path(source).iterdir() if f.suffix.lower() in (".jpg", ".jpeg")]
        if not files:
            print("No JPEG files found on the floppy drive.")
            return False
        for file in files:
            print(f"Copying {file} to {destination}")
            shutil.copy(file, destination)
        return True
    except Exception as e:
        print(f"Error copying files: {e}")
        return False


def delete_lock_file():
    for i in range(1, 4):
        try:
            if os.path.exists(constants.LOCK_FILE):
                os.remove(constants.LOCK_FILE)
            return
        except Exception as e:
            print(f"Error deleting lock file: {e}")
            print(f"Retrying to delete lock file (attempt {i})...")
            time.sleep(1)

    print("Failed to delete lock file after 3 attempts. Please check manually.")


def handleButtonA():
    print("-- Handling Button A Press --")

    print("Creating lock file")
    with open(constants.LOCK_FILE, "w") as f:
        f.write("locked")

    print("Mounting USB floppy drive")
    mount_dir = mount_usb_floppy()
    if not mount_dir:
        print("Failed to mount floppy drive. Aborting.")
        delete_lock_file()
        return

    print("Deleting old images from shared folder")
    if not delete_old_images():
        print("Failed to delete old images. Continuing.")

    print("Copying new images from floppy to shared folder")
    if not copy_new_images(mount_dir):
        print("Failed to copy new images. Aborting.")
        unmount_usb_floppy()
        delete_lock_file()
        return

    print("Successfully copied new images. Unmounting floppy drive.")
    unmount_usb_floppy()

    print("Cleaning up lock file")
    delete_lock_file()

    print("-- Finished Handling Button A Press --")


def onButtonPress(label):
    print(f"Button {label} was pressed!")
    if label == "A":
        handleButtonA()


# Start with a clean slate by ensuring the lock file is removed before we begin
delete_lock_file()

print("Waiting for button presses...")
try:
    buttons.begin(onButtonPress)
except KeyboardInterrupt:
    print("\nShutting down...")
