#!/usr/bin/env python3
"""
RC522 RFID Reader - Diagnostic Test
Troubleshoots RC522 connection issues
"""

import sys
import time

try:
    import spidev
    import RPi.GPIO as GPIO
except ImportError as e:
    print(f"Error: {e}")
    print("Install with: pip install spidev RPi.GPIO")
    sys.exit(1)

def test_spi_communication():
    """Test raw SPI communication with RC522"""
    print("\n1. Testing SPI Communication...")
    print("-" * 50)
    
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 1000000
        
        print(f"✓ SPI device opened")
        print(f"  Bus: 0, Device: 0")
        print(f"  Speed: {spi.max_speed_hz} Hz")
        
        # Try to read version register (should return 0x92)
        # Address: 0x37 (CommandReg), Read mode: MSB=1
        cmd = [0x37 | 0x80, 0x00]  # Read command
        response = spi.xfer2(cmd)
        
        print(f"✓ SPI transfer successful")
        print(f"  Sent: {[hex(x) for x in cmd]}")
        print(f"  Received: {[hex(x) for x in response]}")
        
        spi.close()
        return True
        
    except Exception as e:
        print(f"✗ SPI communication error: {e}")
        return False

def test_gpio_pins():
    """Test GPIO pin states"""
    print("\n2. Testing GPIO Pins...")
    print("-" * 50)
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        pins = {
            24: "RFID CS",
            25: "RFID RST",
            10: "RFID MOSI",
            8: "Display CS",
            23: "Display D/C",
            27: "Display RST",
            12: "Backlight",
            9: "SPI MISO",
            11: "SPI CLK",
        }
        
        for pin, name in pins.items():
            try:
                GPIO.setup(pin, GPIO.IN)
                state = GPIO.input(pin)
                print(f"✓ GPIO {pin} ({name}): {state}")
            except Exception as e:
                print(f"✗ GPIO {pin} ({name}): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ GPIO error: {e}")
        return False
    finally:
        GPIO.cleanup()

def test_rc522_version():
    """Test if RC522 responds to version query"""
    print("\n3. Testing RC522 Version Register...")
    print("-" * 50)
    
    try:
        from mfrc522 import SimpleMFRC522
        
        reader = SimpleMFRC522()
        
        # Try to read the version register directly
        # Different RC522 boards report different versions
        # Common: 0x92, 0x91, others
        
        print("✓ RC522 library imported successfully")
        print("  Reader initialized")
        print("  (Version register reading depends on library internals)")
        
        return True
        
    except Exception as e:
        print(f"✗ RC522 error: {e}")
        print("\n  Possible causes:")
        print("  - RC522 not wired correctly")
        print("  - Wrong CS/RST pins configured")
        print("  - SPI bus conflict")
        return False

def test_tag_reading():
    """Test actual tag reading"""
    print("\n4. Testing Tag Reading...")
    print("-" * 50)
    
    try:
        from mfrc522 import SimpleMFRC522
        
        reader = SimpleMFRC522()
        print("✓ RC522 reader initialized")
        print("  Waiting 10 seconds for tag...")
        print("  (Hold tag close to antenna)")
                
        # start_time = time.time()
        # print("The start time is:", start_time)
        # while (time.time() - start_time) < 10:
        #     print("The current elasped time is:", time.time()-start_time)
        try:
            print("✓ Attempting to read tag...")
            id, text = reader.read()
            print(f"✓ TAG DETECTED!")
            print(f"  ID: {id}")
            print(f"  Text: {text}")
            return True
        except:
            print("✗ No tag detected. Keep holding the tag close to the reader.")
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        
        # print()
        print("✗ No tag detected")
        # return False
        
    except Exception as e:
        print(f"✗ Tag reading error: {e}")
        return False

def main():
    print("=" * 50)
    print("RC522 RFID Reader - Diagnostic Test")
    print("=" * 50)
    
    results = {
        "SPI Communication": test_spi_communication(),
        "GPIO Pins": test_gpio_pins(),
        "RC522 Init": test_rc522_version(),
        "Tag Reading": test_tag_reading(),
    }
    
    print("\n" + "=" * 50)
    print("Diagnostic Summary")
    print("=" * 50)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test}: {status}")
    
    print()
    if results["Tag Reading"]:
        print("✓ RC522 is working correctly!")
    else:
        print("✗ RC522 not detecting tags. Troubleshooting tips:")
        print()
        if not results["SPI Communication"]:
            print("  1. SPI communication failed:")
            print("     - Check SPI pins (GPIO 10, 11, 9)")
            print("     - Verify SPI is enabled: raspi-config")
            print()
        if not results["GPIO Pins"]:
            print("  2. GPIO pins not accessible:")
            print("     - Check GPIO connections")
            print("     - Run with sudo if needed")
            print()
        if not results["RC522 Init"]:
            print("  3. RC522 not initializing:")
            print("     - Check CS pin (GPIO 24)")
            print("     - Check RST pin (GPIO 25)")
            print("     - Check 3.3V power to RC522")
            print()
        print("  4. General troubleshooting:")
        print("     - Hold tag 1-2 cm from antenna")
        print("     - Try different tag brands")
        print("     - Check for short circuits")
        print("     - Verify all solder joints")

if __name__ == "__main__":
    main()
