#!/usr/bin/env python3
"""
Test SPI Devices
Verifies that both SPI devices (RFID and Display) are accessible
"""

import spidev
import sys

def test_spi_device(bus, device):
    """Test if an SPI device can be opened"""
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        max_speed = spi.max_speed_hz
        spi.close()
        print(f"✓ SPI {bus}.{device} opened successfully (max speed: {max_speed} Hz)")
        return True
    except Exception as e:
        print(f"✗ SPI {bus}.{device} error: {e}")
        return False

def main():
    print("=" * 50)
    print("RFID Player - SPI Device Test")
    print("=" * 50)
    print()
    
    print("Testing SPI devices...")
    print()
    
    # Test SPI 0.0 (RFID)
    result_0_0 = test_spi_device(0, 0)
    
    # Test SPI 0.1 (Display)
    result_0_1 = test_spi_device(0, 1)
    
    print()
    
    if result_0_0 and result_0_1:
        print("✓ All SPI devices are accessible!")
        print("  Ready for RFID and Display testing.")
        return 0
    else:
        print("✗ Some SPI devices failed!")
        print("  Check GPIO connections and SPI configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
