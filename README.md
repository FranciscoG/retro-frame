# retro-frame


## Disable the constant clicking sound of the floppy

I plugged my floppy drive via USB into the Pi and it started making a clicking noise at a steady interval. Turns out that this is the only way that linux knows how to check if a disk is inserted, read more about that [here](https://capnfabs.net/posts/why-is-this-floppy-disk-drive-clicking-incessantly/)

I had originally planned to have this project auto-detect disk insert and eject, but given that there's no good way around this, I've decided to disable the constant polling and instead I'll use one of the buttons that comes with the Inky display to indicate that new disk was inserted (for now).

### So here's how to disable the constant polling

First, find your device:
```sh
lsblk
```
Look for something starting with `sd`, mine was `sda`

`sd` stands for SCSI disk, historically for SCSI drives, but Linux uses the same driver (`sd`) for all USB mass storage devices too. The `a` just means it's the first disk of that type detected. A second one would be `sdb`, and so on.

Next, disable polling immediately, this is only temporary but will stop the annoying sound:
```sh
echo 0 | sudo tee /sys/block/sda/events_poll_msecs
```

Now make it permanent with a udev rule. First get the USB vendor/product IDs:
```sh
lsusb
```

Look for your floppy drive (it should say "floppy" somewhere) and note the ID, mine was this`0644:0000`.

Create the rule. Here's a one-liner that will do this for you. Notice where **my** `sda` and `0644:0000` are in this one-liner and replace it with yours:
```sh
echo 'ACTION=="add", KERNEL=="sda", SUBSYSTEMS=="usb", ATTRS{idVendor}=="0644", ATTRS{idProduct}=="0000", ATTR{events_poll_msecs}="0"' | sudo tee /etc/udev/rules.d/99-no-floppy-poll.rules

# confirm that it wrote to the file
cat /etc/udev/rules.d/99-no-floppy-poll.rules
```

Then reload:
```sh
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Setting up to work with the display

The creators of the Pimoroni Inky display have also developed a python libray for it. You can find it on [github](https://github.com/pimoroni/inky) and follow the instructions on how to set it up.

Being that I'm using a Pi Zero W, I needed to do some extra steps that I found in [this github issue](https://github.com/pimoroni/inky/issues/220#issuecomment-3393634874):

```sh
sudo apt update && sudo apt upgrade -y
# note, I added libopenblas0 to this list because it was necessary in the end
sudo apt-get install git python3-pandas python3-numpy libopenblas0
git clone https://github.com/pimoroni/inky.git
cd inky/
./install.sh

# It might ask you this:
# "This script should be run in a virtual Python environment."
# "Would you like us to create and/or use a default one? [y/N]"
# choose Yes
# I also chose to installing examples and any other question it asked me

sudo reboot
```

Then start the python virtual environment
```sh
source ~/.virtualenvs/pimoroni/bin/activate
```

[source](https://github.com/pimoroni/inky/issues/220#issuecomment-3393634874)

## Setting up the floppy daemon

### Prevent the need for password

If you run `python3 floppy-loader.py` and test it out, you'll notice that it will ask you for your Pi's password in order to mount the USB floppy drive. That's no fun so we need to fix it so we don't need the password for that.

To do that, we need to add a `polkit rule`, replace `pi-frame` with your Pi's user name:

```sh
sudo tee /etc/polkit-1/rules.d/10-udisks-floppy.rules > /dev/null <<'EOF'
polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.udisks2.filesystem-mount" ||
          action.id == "org.freedesktop.udisks2.filesystem-mount-other-seat" ||
          action.id == "org.freedesktop.udisks2.filesystem-unmount-others") &&
        subject.user == "pi-frame") {
        return polkit.Result.YES;
    }
});
EOF

# confirm
cat /etc/polkit-1/rules.d/10-udisks-floppy.rules
```

Test it by running the script again, it should mount without a password now. 

### Add the service

Replace "pi-frame" with your user name:
```sh
sudo tee /etc/systemd/system/floppy-loader.service > /dev/null <<'EOF'
[Unit]
Description=Floppy Loader Daemon
After=network.target

[Service]
Type=simple
User=pi-frame
WorkingDirectory=/home/pi-frame/retro-frame
ExecStart=/home/pi-frame/retro-frame/floppy-loader.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# confirm
cat /etc/systemd/system/floppy-loader.service
```

Then:
```sh
sudo systemctl daemon-reload
sudo systemctl enable --now floppy-loader.service
sudo systemctl status floppy-loader.service
```

Watch logs with:
```sh
journalctl -u floppy-loader.service -f
```