#!/usr/bin/env python3
"""
Potentiometer Testing Script
Test volume potentiometer via PCF8591 ADC
"""

import sys
import time

try:
    from src.potentiometer_handler import PotentiometerHandler
    from config.gpio_config import PCF8591_I2C_ADDRESS, PCF8591_CHANNEL_VOLUME, PCF8591_I2C_BUS
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you're running from the project root directory with the virtual environment activated")
    print("Also ensure smbus is installed: pip install smbus-cffi")
    sys.exit(1)

def main():
    print("=" * 60)
    print("POTENTIOMETER TESTING - Volume Control")
    print("=" * 60)
    print()
    print("PCF8591 Configuration:")
    print(f"  I2C Bus: {PCF8591_I2C_BUS}")
    print(f"  Address: 0x{PCF8591_I2C_ADDRESS:02x}")
    print(f"  Channel: AIN{PCF8591_CHANNEL_VOLUME} (Volume)")
    print()
    print("Initializing potentiometer handler...")
    print()
    
    # Create potentiometer handler
    try:
        pot_handler = PotentiometerHandler(
            i2c_bus=PCF8591_I2C_BUS,
            pcf8591_address=PCF8591_I2C_ADDRESS,
            channel=PCF8591_CHANNEL_VOLUME,
            deadzone=3
        )
    except Exception as e:
        print(f"✗ Failed to initialize potentiometer: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure I2C is enabled: raspi-config → Interface Options → I2C")
        print("  2. Check PCF8591 connections: SDA=GPIO2, SCL=GPIO3")
        print("  3. Verify I2C devices: i2cdetect -y 1")
        print("  4. Install smbus: pip install smbus-cffi")
        sys.exit(1)
    
    print("✓ Potentiometer handler initialized")
    print()
    
    # Register callback
    def on_volume_change(raw_value, percentage):
        bar_length = int(percentage / 5)  # 0-100% → 0-20 characters
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  Volume: [{bar}] {percentage:3d}% (raw: {raw_value:3d})")
    
    pot_handler.set_callback(on_volume_change)
    
    print("-" * 60)
    print()
    print("Instructions:")
    print("  - Turn the potentiometer knob slowly")
    print("  - Watch the volume level update in real-time")
    print("  - Press Ctrl+C to stop testing")
    print()
    print("Waiting for potentiometer input...")
    print()
    
    # Start polling
    pot_handler.start()
    
    try:
        # Run test for up to 5 minutes or until interrupted
        start_time = time.time()
        timeout = 300  # 5 minutes
        
        while time.time() - start_time < timeout:
            time.sleep(0.1)
        
        print()
        print("Test timeout (5 minutes)")
        
    except KeyboardInterrupt:
        print()
        print()
        print("✓ Test interrupted by user")
    
    finally:
        print()
        print("-" * 60)
        print("Cleaning up...")
        pot_handler.cleanup()
        
        # Final reading
        final_value = pot_handler.read_once()
        print(f"Final volume: {final_value['percentage']}% (raw: {final_value['raw']})")
        print("✓ Potentiometer test complete")

if __name__ == "__main__":
    main()
