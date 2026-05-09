# Plan

## Hardware

- Raspberry Pi Zero WH running `Raspbian GNU/Linux 13 (trixie, debian 13.4)`
- Pimoroni Inky Impression 7.3" display (Spectra 6 variant — 6 colors, no orange)
- USB floppy drive enclosure
- Power supply

## Software

- Python (in a virtualenv at `~/.virtualenvs/pimoroni/`)
- https://github.com/pimoroni/inky

**Shared folder** — `/home/pi-frame/photos/` is where images live and where the slideshow reads from

**Lock file** — `/tmp/floppy.lock` signals that a floppy load is in progress so the slideshow shows a loading screen instead of cycling

## Architecture

A single long-running program (`main.py`) plus a one-shot helper script (`floppy_loader.py`).

- `main.py` runs the slideshow on the main thread and a button listener on a daemon thread. 
- When a button is pressed, the button thread fires a callback. 
  - Button A spawns `floppy_loader.py` as a detached subprocess so the slideshow keeps running.

```
main.py
├── main thread     → slideshow loop (reads photos, drives display)
└── daemon thread   → button listener (gpiod)
                          ├── Button A → subprocess.Popen(./floppy_loader.py)
                          └── Button B → slideshow.skip()  (planned)
```

The slideshow and `floppy_loader.py` communicate only through the lock file: floppy_loader creates it on start and deletes it on exit; the slideshow polls for its presence.

## Slideshow loop (`slideshow.py`)

- Runs forever
- Each iteration:
  - If lock file is present → draw loading screen (once) and sleep 5s
  - Else → load next image from shared folder, display it, sleep 60s
  - If shared folder is empty → draw the default image
- Skips redrawing the same default/loading screen on consecutive iterations to spare e-ink refreshes

## Floppy loader script (`floppy_loader.py`)

A standalone executable script. Triggered on demand, exits when done.

- Create lock file
- Mount the floppy disk via `udisksctl` (no sudo, allowed by polkit rule)
- Delete old images from shared folder
- Copy new JPEG images from the floppy
- Unmount the floppy
- Delete lock file
- Exit

If any critical step fails (mount, copy), it cleans up (unmounts if needed, removes lock) and exits.

## Display states

- **Default image** — a synthwave-style scene drawn with PIL (yellow sun with horizontal bars, red perspective grid, white horizon line on black). Shown when the shared folder is empty.
- **Loading screen** — "Loading..." text, shown while the lock file is present.
- **Slideshow** — cycles through all images in the shared folder, 60 seconds per image.

## Buttons

The Inky has 4 buttons, A–D. We use 2:

- **Button A** — trigger floppy load (spawns `floppy_loader.py`, ignored if a load is already in progress)
- **Button B** — skip to the next image (planned, not yet implemented)
