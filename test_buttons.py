#!/usr/bin/env python3
"""
Button Testing Script
Test all 4 buttons to verify they work correctly
"""

import sys
import time

try:
    from src.button_handler import ButtonHandler
    from config.gpio_config import BUTTON_PLAY_PAUSE, BUTTON_NEXT, BUTTON_PREV, BUTTON_SHUFFLE
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you're running from the project root directory with the virtual environment activated")
    sys.exit(1)

def main():
    print("=" * 60)
    print("BUTTON TESTING - 4 Button Test")
    print("=" * 60)
    print()
    print("GPIO Pin Configuration:")
    print(f"  Button 1 (Play/Pause) → GPIO {BUTTON_PLAY_PAUSE}")
    print(f"  Button 2 (Next)       → GPIO {BUTTON_NEXT}")
    print(f"  Button 3 (Previous)   → GPIO {BUTTON_PREV}")
    print(f"  Button 4 (Shuffle)    → GPIO {BUTTON_SHUFFLE}")
    print()
    print("Initializing buttons...")
    print()
    
    # Create button handler
    handler = ButtonHandler(debounce_ms=50)
    
    # Register buttons with their callbacks
    def button_callback(event):
        timestamp = time.strftime("%H:%M:%S", time.localtime(event.press_time))
        print(f"✓ [{timestamp}] BUTTON PRESSED: {event.button_name:20} (GPIO {event.gpio_pin})")
    
    # Register all 4 buttons
    handler.register_button(1, BUTTON_PLAY_PAUSE, "Play/Pause")
    handler.register_button(2, BUTTON_NEXT, "Next")
    handler.register_button(3, BUTTON_PREV, "Previous")
    handler.register_button(4, BUTTON_SHUFFLE, "Shuffle")
    
    # Set callbacks for all buttons
    for button_id in [1, 2, 3, 4]:
        handler.set_button_callback(button_id, button_callback)
    
    # Start polling
    handler.start()
    
    print("✓ All buttons initialized and polling started")
    print()
    print("Instructions:")
    print("  - Press each button one at a time")
    print("  - Verify the button name appears on screen")
    print("  - Press Ctrl+C to stop testing")
    print()
    print("Waiting for button presses...")
    print("-" * 60)
    print()
    
    try:
        # Run test for up to 5 minutes or until interrupted
        start_time = time.time()
        timeout = 300  # 5 minutes
        presses = {1: 0, 2: 0, 3: 0, 4: 0}
        
        while time.time() - start_time < timeout:
            time.sleep(0.5)
            
            # Check periodically if we've detected all 4 buttons
            # (This will update as callbacks fire)
        
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
        handler.cleanup()
        print("✓ Button test complete")

if __name__ == "__main__":
    main()
