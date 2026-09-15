# Setup Guide

## Raspberry Pi Packages

```bash
sudo apt update
sudo apt install -y git mpv unzip python3-venv python3-dev python3-rpi.gpio
```

Enable SPI and I2C:

```bash
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
```

## Python Environment

```bash
cd ~/Offline_RFID_Music_Player
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Hardware Checks

```bash
ls -l /dev/spidev*
i2cdetect -y 1
aplay -l
```

Run hardware diagnostics from the project root:

```bash
python3 sandbox/test_rfid_quick.py
python3 sandbox/test_buttons.py
python3 sandbox/test_potentiometer.py
python3 sandbox/test_button_led_integration.py
```

## Music and RFID Mapping

Upload music to the Pi, then register an album directory:

```bash
python3 src/multi_tag_rfid_playlist_controls.py \
  --register 1053655409858 \
  /home/neonkon/Music/mac-miller-swimming
```

This creates or refreshes `tracklist.txt` and stores the mapping in `data/rfid_library.db`.

Start the player:

```bash
python3 src/multi_tag_rfid_playlist_controls.py
```

## Software Tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Shutdown

Press `Ctrl+C`. The controller should stop RFID polling, terminate mpv, clean up GPIO/I2C resources, and remove `/tmp/rfid-mpv.sock`.
