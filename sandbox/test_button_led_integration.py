#!/usr/bin/env python3
"""
Button + LED Integration Test
Test shuffle button with LED indicator
"""

import sys
import time

try:
    from src.button_handler import ButtonHandler
    from src.led_handler import LEDHandler
    from config.gpio_config import BUTTON_SHUFFLE, LED_SHUFFLE
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you're running from the project root directory with the virtual environment activated")
    sys.exit(1)

# Global state
shuffle_state = False
led_handler = None

def on_shuffle_button_pressed(event):
    """Callback when shuffle button is pressed"""
    global shuffle_state
    
    # Toggle shuffle state
    shuffle_state = not shuffle_state
    
    # Update LED to reflect new state
    led_handler.set_state("shuffle", shuffle_state)
    
    # Print status
    status = "ON" if shuffle_state else "OFF"
    timestamp = time.strftime("%H:%M:%S", time.localtime(event.press_time))
    print(f"[{timestamp}] Shuffle Button Pressed → Shuffle is now: {status} (LED {'ON' if shuffle_state else 'OFF'})")

def main():
    global led_handler
    
    print("=" * 60)
    print("SHUFFLE BUTTON + LED INTEGRATION TEST")
    print("=" * 60)
    print()
    print("GPIO Configuration:")
    print(f"  Shuffle Button → GPIO {BUTTON_SHUFFLE}")
    print(f"  Shuffle LED    → GPIO {LED_SHUFFLE}")
    print()
    print("Initializing button handler and LED handler...")
    print()
    
    # Create handlers
    button_handler = ButtonHandler(debounce_ms=50)
    led_handler = LEDHandler()
    
    # Register shuffle button
    button_handler.register_button(4, BUTTON_SHUFFLE, "Shuffle")
    
    # Register shuffle LED (starts OFF)
    led_handler.register_led("shuffle", LED_SHUFFLE, initial_state=False)
    
    # Set button callback
    button_handler.set_button_callback(4, on_shuffle_button_pressed)
    
    # Start polling
    button_handler.start()
    
    print("✓ Button and LED initialized")
    print()
    print("-" * 60)
    print()
    print("Instructions:")
    print("  - Press the shuffle button to toggle shuffle on/off")
    print("  - Watch the LED turn on/off accordingly")
    print("  - Press Ctrl+C to stop testing")
    print()
    print("Current Shuffle State: OFF")
    print()
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print()
        print()
        print("✓ Test interrupted by user")
    
    finally:
        print()
        print("-" * 60)
        print("Cleaning up...")
        button_handler.cleanup()
        led_handler.cleanup()
        print("✓ Integration test complete")
        print(f"Final shuffle state: {'ON' if shuffle_state else 'OFF'}")

if __name__ == "__main__":
    main()
