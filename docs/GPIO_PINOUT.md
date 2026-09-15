# GPIO Pinout

The RFID library uses BOARD numbering internally. The shared configuration also records BCM equivalents for clarity.

## RFID RC522

| Function | BCM GPIO | Physical pin |
|---|---:|---:|
| CS/SDA | 8 | 24 |
| Reset | 25 | 22 |
| MOSI | 10 | 19 |
| MISO | 9 | 21 |
| SCLK | 11 | 23 |
| 3.3V | - | 1 |
| GND | - | 6 |

## Buttons

| Function | BCM GPIO | BOARD pin |
|---|---:|---:|
| Play/Pause | 26 | 37 |
| Next | 6 | 31 |
| Previous | 5 | 29 |
| Shuffle | 22 | 15 |

## Shuffle LED

| Function | BCM GPIO | BOARD pin |
|---|---:|---:|
| Shuffle status | 27 | 13 |

## Potentiometer

The PCF8591 ADC is connected over I2C:

- Bus: 1
- Address: `0x48`
- Volume channel: AIN0
- SDA: BCM GPIO 2, physical pin 3
- SCL: BCM GPIO 3, physical pin 5

Pin constants are maintained in `config/gpio_config.py`.
