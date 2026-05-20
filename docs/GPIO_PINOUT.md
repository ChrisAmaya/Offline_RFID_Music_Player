"""
GPIO Pin Configuration Documentation
=====================================

**Hardware Setup (Revised - Display Removed):**
- Raspberry Pi 3B (40-pin GPIO header)
- RFID-RC522 reader on SPI0
- 5 Physical buttons on GPIO (TBD - planning phase)
- HiFiBerry DAC+ Light (via I2S audio output)
- USB CD/DVD reader (external)

**Updated Scope:**
- No TFT display (replaced with physical album artwork labels)
- RFID-only SPI configuration (GPIO 24 for CS, GPIO 25 for RST)
- SPI bus no longer shared - RFID has exclusive access

**RFID Reader (RC522) - SPI0 Configuration:**
- SPI Clock (CLK): GPIO 11 (Physical Pin 23)
- SPI MOSI (DIN): GPIO 10 (Physical Pin 19)
- SPI MISO (DOUT): GPIO 9 (Physical Pin 21)
- RFID Chip Select (SDA): GPIO 8 (Physical Pin 24)
- RFID Reset (RST): GPIO 25 (Physical Pin 22)
- RFID VCC: 3.3V (Pin 1 or 17)
- RFID GND: GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)

**Button Assignments (TBD - Planning Phase):**
- GPIO 17: PLAY/PAUSE (proposed)
- GPIO 22: PREVIOUS (proposed)
- GPIO 27: NEXT (proposed)
- GPIO 18: SHUFFLE (proposed)
- GPIO 23: VOLUME UP (proposed)
- (6th button TBD or use potentiometer for volume)

**Pinout Reference (40-pin GPIO Header):**
```
Pin 1  (3V3)   → RFID VCC
Pin 2  (5V)    → [Not used - 5V not needed]
Pin 3  (GPIO 2 SDA)  → [I2C - HiFiBerry uses I2S, not I2C]
Pin 4  (5V)
Pin 5  (GPIO 3 SCL)  → [I2C]
Pin 6  (GND)   → RFID GND
Pin 7  (GPIO 4)      → [Available]
Pin 8  (GPIO 14 TX)  → [Serial]
Pin 9  (GND)   → Common GND
Pin 10 (GPIO 15 RX) → [Serial]
Pin 11 (GPIO 17)    → [Button: PLAY/PAUSE]
Pin 12 (GPIO 18)    → [Button: SHUFFLE]
Pin 13 (GPIO 27)    → [Button: NEXT]
Pin 14 (GND)
Pin 15 (GPIO 22)    → [Button: PREVIOUS]
Pin 16 (GPIO 23)    → [Button: VOLUME UP]
Pin 17 (3V3)
Pin 18 (GPIO 24)    → [Available]
Pin 19 (GPIO 10)    → SPI MOSI (RFID DIN)
Pin 20 (GND)
Pin 21 (GPIO 9)     → SPI MISO (RFID DOUT)
Pin 22 (GPIO 25)    → RFID RST
Pin 23 (GPIO 11)    → SPI CLK (RFID CLK)
Pin 24 (GPIO 8)     → RFID CS (SDA)
Pin 25 (GND)
Pin 26 (GPIO 7)     → [SPI CE1 - available]
Pin 27 (GPIO 0 SDA) → [I2C]
Pin 28 (GPIO 1 SCL) → [I2C]
Pin 29 (GPIO 5)     → [Available]
Pin 30 (GND)
Pin 31 (GPIO 6)     → [Available]
Pin 32 (GPIO 12)    → [Available - was display backlight PWM]
Pin 33 (GPIO 13)    → [Available]
Pin 34 (GND)
Pin 35 (GPIO 19)    → [SPI MISO alt - not used]
Pin 36 (GPIO 16)    → [Available]
Pin 37 (GPIO 26)    → [Available]
Pin 38 (GPIO 20)    → [Available]
Pin 39 (GND)
Pin 40 (GPIO 21)    → [Available]
```

**I2S Audio Output (HiFiBerry DAC+):**
- Uses standard Raspberry Pi I2S pins (GPIO 18 BCM, GPIO 19 BCM)
- Configured via device tree overlay
- Audio output on 3.5mm jack on DAC board

**SPI Device Files:**
- /dev/spidev0.0 → RFID reader

**Testing Commands:**
```bash
# Check GPIO configuration
raspi-gpio get

# Test SPI device accessibility
ls -la /dev/spidev*

# Test I2S audio
cat /proc/asound/cards

# Check hardware configuration
vcgencmd measures_temp
```

**Notes:**
- Button pins subject to change during integration phase
- Volume control may use potentiometer (analog) or PWM digital control
- CD player uses external USB reader (no GPIO required)
- All audio routed through HiFiBerry DAC+
"""
