"""
GPIO Pin Configuration Documentation
=====================================

Hardware Setup:
- Raspberry Pi 3B (40-pin GPIO header)
- RFID-RC522 on SPI0
- 3.5" TFT Display on SPI0 (different CS pin)
- 5 Physical buttons on GPIO
- HiFiBerry DAC+ Light (via I2S)

SPI Bus Sharing:
Both RFID and TFT use SPI0. They are isolated by different Chip Select (CS) pins:
- RFID CS: GPIO 24
- Display CS: GPIO 8
- SPI Clock (CLK): GPIO 11
- SPI MOSI (DIN): GPIO 10
- SPI MISO (DOUT): GPIO 9

Pinout Reference (40-pin DIP):
```
    3V3  1 |□ □| 2  5V
    SDA  3 |□ □| 4  5V
    SCL  5 |□ □| 6  GND
      7  7 |□ □| 8  CS(TFT)
     GND  9 |□ □|10  MOSI
    MISO 11 |□ □|12  PWM(Backlight)
      17 13 |□ □|14  GND
      27 15 |□ □|16  23(DC)
    3V3 17 |□ □|18  22(PREV)
    MOSI 19 |□ □|20  GND
     5  21 |□ □|22  26(SHUFFLE)
    CLK 23 |□ □|24  CS(RFID)
     GND 25 |□ □|26  24(RST-RFID)
     SDA 27 |□ □|28  SCL
      17 29 |□ □|30  GND
    RST 31 |□ □|32  VOLUP
     GND 33 |□ □|34  GND
    MOSI 35 |□ □|36  NEXT
      26 37 |□ □|38  VOLDOWN
     GND 39 |□ □|40  PLAY
```

Button Assignments:
- GPIO 17: PLAY/PAUSE
- GPIO 18: NEXT
- GPIO 22: PREVIOUS
- GPIO 26: SHUFFLE
- GPIO 5: VOLUME UP
- GPIO 6: VOLUME DOWN

Testing Commands:
```bash
# List GPIO pins
raspi-gpio get

# Test SPI
lsmod | grep spi

# Test I2S (HiFiBerry)
cat /proc/asound/cards
```
"""
