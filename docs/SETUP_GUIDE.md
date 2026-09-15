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

## Automatic Startup with systemd

The repository includes `systemd/rfid-player.service`. Install it on the Pi after the repository, virtual environment, and music are ready:

```bash
cd ~/Offline_RFID_Music_Player
sudo cp systemd/rfid-player.service /etc/systemd/system/rfid-player.service
sudo systemctl daemon-reload
sudo systemctl enable rfid-player.service
sudo systemctl start rfid-player.service
```

Check whether it started:

```bash
sudo systemctl status rfid-player.service
```

Follow live service output while debugging:

```bash
sudo journalctl -u rfid-player.service -f
```

The service automatically restarts after an unexpected failure because of `Restart=on-failure`.

## Application Logs

The Python runtime writes to:

```text
~/Offline_RFID_Music_Player/logs/rfid-player.log
```

The log rotates at 2 MB and keeps 5 backups, for a maximum of approximately 12 MB. View recent entries with:

```bash
tail -n 100 ~/Offline_RFID_Music_Player/logs/rfid-player.log
```

To inspect the service and application logs together:

```bash
sudo journalctl -u rfid-player.service -n 100 --no-pager
tail -n 100 ~/Offline_RFID_Music_Player/logs/rfid-player.log
```

## Manual Start and Shutdown

For interactive debugging, stop systemd first:

```bash
sudo systemctl stop rfid-player.service
source ~/Offline_RFID_Music_Player/venv/bin/activate
cd ~/Offline_RFID_Music_Player
python3 -u src/multi_tag_rfid_playlist_controls.py
```

Press `Ctrl+C` to stop the manual process. The controller should stop RFID polling, terminate mpv, clean up GPIO/I2C resources, and remove `/tmp/rfid-mpv.sock`.

To stop the managed service:

```bash
sudo systemctl stop rfid-player.service
```

To disable automatic startup:

```bash
sudo systemctl disable rfid-player.service
```

## Remote Pi Maintenance Workflow

The player can run as a systemd service while you connect to the Raspberry Pi over SSH. Stop the player before changing music or the SQLite mapping database.

### 1. SSH into the Raspberry Pi

Using the Pi hostname:

```bash
ssh neonkon@raspberrypi.local
```

Using the current local-network IP address:

```bash
ssh neonkon@172.16.1.163
```

### 2. Stop the Player

Run these commands on the Pi:

```bash
sudo systemctl stop rfid-player.service
sudo systemctl status rfid-player.service
```

The status should show `inactive (dead)` before modifying the music library or database.

### 3. Upload Music with scp

Run this command on the local computer, not inside the SSH session:

```bash
scp "/home/neonkon/Music/Mac Miller.zip" \
  neonkon@172.16.1.163:/home/neonkon/Music/
```

Reconnect to the Pi if necessary and extract the archive:

```bash
cd ~/Music
unzip "Mac Miller.zip"
```

Confirm the album directory and audio files exist:

```bash
find ~/Music -maxdepth 2 -type f -iname '*.mp3' | sort
```

### 4. Update RFID Mapping Data

From the project directory on the Pi, register the tag against the actual album directory:

```bash
cd ~/Offline_RFID_Music_Player
source venv/bin/activate

python3 src/multi_tag_rfid_playlist_controls.py \
  --register 1053655409858 \
  /home/neonkon/Music/mac-miller-swimming
```

Registration will create or refresh:

```text
/home/neonkon/Music/mac-miller-swimming/tracklist.txt
```

Verify the mapping and generated playlist:

```bash
cat /home/neonkon/Music/mac-miller-swimming/tracklist.txt

python3 - <<'PY'
import sqlite3

with sqlite3.connect("data/rfid_library.db") as db:
    print(db.execute("""
        SELECT tag_mappings.tag_id, content.name, content.path
        FROM tag_mappings
        JOIN content ON content.id = tag_mappings.content_id
        ORDER BY tag_mappings.tag_id
    """).fetchall())
PY
```

Replace the tag ID and album path for each additional mapping. Tag registration accepts decimal IDs and hexadecimal serial forms such as `35:49:C0:A4`.

### 5. Start the Player

After the music and mappings are ready:

```bash
sudo systemctl start rfid-player.service
sudo systemctl status rfid-player.service
```

Follow the startup and RFID logs:

```bash
sudo journalctl -u rfid-player.service -f
```

The player should wait for an RFID tag. It starts mpv only after a mapped tag is detected.

### 6. Leave the SSH Session

The player continues running after disconnecting SSH because systemd owns the process:

```bash
exit
```
