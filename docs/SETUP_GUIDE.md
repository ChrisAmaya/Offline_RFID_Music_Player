# Setup Guide - RFID/CD Music Player

## Hardware Assembly Checklist

### Phase 1: Basic Assembly
- [ ] Connect Raspberry Pi 3B power supply (5V/2.5A)
- [ ] Insert OS microSD card into Pi
- [ ] Connect 3.5" TFT display to GPIO (40-pin connector)
- [ ] Connect RFID-RC522 via Dupont wires to SPI/GPIO
- [ ] Connect 5 buttons to designated GPIO pins
- [ ] Verify all connections are secure

### Phase 2: Audio Setup
- [ ] Install HiFiBerry DAC+ Light onto GPIO (I2S pins 12, 35, 40)
- [ ] Connect audio output (RCA) from DAC to amplifier/speakers
- [ ] Connect USB audio interface (if using) or verify DAC detection

### Phase 3: CD Drive Integration
- [ ] Connect USB CD/DVD reader to Pi USB port
- [ ] Test disc detection in OS

### Phase 4: Power Management
- [ ] Verify all devices receive stable power
- [ ] Check for brownout/voltage sag indicators
- [ ] Optionally install powered USB hub if instability detected

## Software Installation

### 1. Raspberry Pi OS Installation
```bash
# Use Raspberry Pi Imager to write OS to microSD
# Select: Raspberry Pi OS Lite (32-bit or 64-bit)
# Configure: SSH enabled, default user
```

### 2. Initial Raspberry Pi Configuration
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Run raspi-config
sudo raspi-config

# Configure:
# - Enable SPI (Advanced Options > SPI)
# - Enable I2C (Advanced Options > I2C)
# - Set GPU memory (Advanced Options > GPU Memory to 128MB minimum)
# - Enable SSH
```

### 3. Clone Repository
```bash
cd ~
git clone <your-github-repo-url>
cd RFID_Player
chmod +x setup.sh
```

### 4. Run Setup Script
```bash
./setup.sh
```

This will:
- Update system packages
- Install Python dependencies
- Install system libraries (mpv, libcdio, etc.)
- Create data directories
- Configure SPI/I2C

### 5. Activate Virtual Environment
```bash
source venv/bin/activate
```

## Hardware Testing

### Test SPI Bus (TFT + RFID)
```bash
# Check SPI is enabled
ls -la /dev/spidev*

# Should show:
# /dev/spidev0.0
# /dev/spidev0.1
```

### Test RFID Reader
```python
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()
try:
    id, text = reader.read()
    print(f"RFID Tag: {id}")
finally:
    GPIO.cleanup()
```

### Test HiFiBerry DAC
```bash
# Check ALSA cards
aplay -l
arecord -l

# You should see HiFiBerry DAC listed
```

### Test TFT Display
```bash
# TFT driver depends on model
# Standard 3.5" SPI displays use ili9486 or st7789 driver
# See docs for specific driver setup
```

### Test Audio Playback
```bash
# Test mpv
mpv /path/to/audio/file.mp3

# Test volume control
amixer set Master 50%
```

## Configuration

Edit configuration files in `config/`:
- `gpio_config.py`: GPIO pin assignments
- `audio_config.py`: Audio player settings
- `database_config.py`: Database paths and schema

## Next Steps

1. See [ARCHITECTURE.md](ARCHITECTURE.md) for software design
2. Run test suite: `python -m pytest tests/`
3. Start main application: `python src/main.py`

## Troubleshooting

### SPI Conflict (TFT + RFID)
- Verify each device has unique CS pin
- Check cable connections
- Test with separate SPI buses if available

### Audio Not Working
- Run: `aplay -l` to verify DAC detection
- Check HiFiBerry driver: `sudo apt-get install hifiberryinstaller`
- Test with: `speaker-test -t wav -c 2 -r 44100`

### Button Debouncing Issues
- Adjust `DEBOUNCE_TIME` in `gpio_config.py`
- Add capacitor (0.1µF) across button pins if noise persists

### CD Drive Not Detected
- Check USB connection
- Run: `lsblk` to verify device
- Install cdparanoia: `sudo apt-get install cdparanoia`

## Performance Tuning

### Reduce Memory Usage
- Use Python's `memory_profiler`
- Monitor with `free -h` and `top -p $(pidof python3)`

### Optimize Boot Time
- Disable unnecessary services: `sudo systemctl disable <service>`
- Profile startup time

### Audio Quality
- Test different sample rates in `audio_config.py`
- Monitor CPU usage during playback with `htop`

## Backup & Maintenance

### Backup microSD Card
```bash
# On host machine
sudo dd if=/dev/sdX bs=1M | gzip > rfid_player_backup.img.gz
```

### Database Maintenance
```bash
# Vacuum database (optimize)
sqlite3 data/jukebox.db "VACUUM;"

# Backup database
cp data/jukebox.db data/jukebox.db.backup
```

## Resources

- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.com/documentation/computers/os.html)
- [MFRC522 Python Library](https://github.com/mxgxw/MFRC522-python)
- [mpv Manual](https://mpv.io/manual/)
- [HiFiBerry Documentation](https://www.hifiberry.com/docs/)
