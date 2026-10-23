# RFID Player Controller PCB Draft

This folder contains the initial electrical netlist for a cable-connected controller board. Import `controller_board.net` into KiCad PCB Editor using **File -> Import -> Netlist** to start PCB placement and routing.

## Included

- J1: 2x20 Raspberry Pi GPIO ribbon-cable connector
- J2: RC522 module header (8 pins)
- J3: PCF8591 module I2C/power header
- J4: Three-wire potentiometer connector to PCF8591 AIN0
- J5-J8: Off-board Play/Pause, Next, Previous, and Shuffle button connectors
- R1 and D1: 330 ohm shuffle LED indicator circuit

Pi pins are taken from `config/gpio_config.py` and its BOARD-numbered equivalents:

| Function | Pi physical pin | BCM GPIO |
|---|---:|---:|
| RFID CS/SDA | 24 | 8 |
| RFID SCLK | 23 | 11 |
| RFID MOSI | 19 | 10 |
| RFID MISO | 21 | 9 |
| RFID reset | 22 | 25 |
| I2C SDA | 3 | 2 |
| I2C SCL | 5 | 3 |
| Play/Pause | 37 | 26 |
| Next | 31 | 6 |
| Previous | 29 | 5 |
| Shuffle button | 15 | 22 |
| Shuffle LED | 13 | 27 |

## Before PCB Fabrication

This is an electrical starting point, **not a fabrication-ready design**. KiCad is not installed in the current development environment, so the netlist has not been opened or validated in KiCad. Open it in KiCad, assign/verify footprints, make the schematic and PCB layout, run ERC/DRC, and export fabrication files only after checking the physical hardware.

In particular:

1. Verify the pin order printed on your exact RC522 and PCF8591 breakout boards. The netlist assumes the common RC522 order `SDA, SCK, MOSI, MISO, IRQ, GND, RST, 3.3V`; verify before connecting power.
2. Verify the potentiometer connector order against the actual PCF8591 module and wiring.
3. Confirm button wiring is active-low to ground, matching `ButtonHandler` pull-ups.
4. Confirm the 330 ohm LED resistor is appropriate for the selected LED and GPIO current; keep GPIO current within Raspberry Pi limits.
5. Choose a keyed, locking connector and board outline based on the enclosure and actual ribbon cable.
6. The board is cable-connected; it is not a HAT and does not stack on the Pi or HiFiBerry. Check connector clearance and HiFiBerry access when planning the Pi-side cable adapter.
7. Keep the board at 3.3 V logic. Do not feed 5 V into Raspberry Pi GPIO, RC522, or PCF8591 signal pins.

Recommended next KiCad work: create a schematic from this netlist, assign footprints matching purchased connectors, define the enclosure/board dimensions, then route and run ERC/DRC.
