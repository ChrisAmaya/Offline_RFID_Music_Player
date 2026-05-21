#!/usr/bin/env python3
"""
Potentiometer Handler Module
Handles analog potentiometer input via PCF8591 ADC
"""

import logging
import threading
import time
from typing import Optional, Callable

try:
    import smbus
except ImportError:
    raise ImportError("smbus library not installed. Install with: pip install smbus-cffi")

# Setup logging
logger = logging.getLogger(__name__)


class PotentiometerHandler:
    """
    Handles analog potentiometer input via PCF8591 ADC
    
    Features:
    - Reads analog values from PCF8591 ADC via I2C
    - Converts raw values (0-255) to percentage (0-100)
    - Configurable deadzone to prevent jitter
    - Event callbacks for value changes
    - Background polling thread
    """
    
    def __init__(self, i2c_bus: int = 1, pcf8591_address: int = 0x48, channel: int = 0, deadzone: int = 3):
        """
        Initialize potentiometer handler
        
        Args:
            i2c_bus: I2C bus number (default 1 for GPIO 2/3)
            pcf8591_address: PCF8591 I2C address (default 0x48)
            channel: ADC channel (0-3, default 0 for AIN0)
            deadzone: Threshold for value change detection (0-255, default 3 for jitter reduction)
        """
        self.i2c_bus = i2c_bus
        self.pcf8591_address = pcf8591_address
        self.channel = channel
        self.deadzone = deadzone
        
        self.bus = None
        self.current_value = 0
        self.current_percentage = 0
        self.callbacks = []
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        
        # Initialize I2C bus
        try:
            self.bus = smbus.SMBus(i2c_bus)
            logger.info(f"✓ PCF8591 initialized on I2C bus {i2c_bus}, address 0x{pcf8591_address:02x}")
        except Exception as e:
            logger.error(f"Failed to initialize I2C bus: {e}")
            raise
    
    def set_callback(self, callback: Callable):
        """
        Set callback function for value changes
        
        Args:
            callback: Function to call when potentiometer value changes
                     Receives (raw_value, percentage) as arguments
        """
        self.callbacks.append(callback)
        logger.info(f"Callback registered for potentiometer (total: {len(self.callbacks)})")
    
    def _read_adc_value(self) -> int:
        """
        Read raw ADC value from PCF8591
        
        Returns:
            Raw ADC value (0-255)
        """
        try:
            # PCF8591 requires a dummy read on first call
            # Then subsequent reads return the previously selected channel
            self.bus.read_byte(self.pcf8591_address)
            
            # Select the desired channel (0-3)
            # Write format: control byte = 0x40 | channel
            self.bus.write_byte(self.pcf8591_address, 0x40 | self.channel)
            
            # Read the value
            value = self.bus.read_byte(self.pcf8591_address)
            return value
            
        except Exception as e:
            logger.error(f"Error reading ADC value: {e}")
            return self.current_value
    
    def _raw_to_percentage(self, raw_value: int) -> int:
        """Convert raw ADC value (0-255) to percentage (0-100)"""
        return int((raw_value / 255.0) * 100)
    
    def start(self):
        """Start background polling thread"""
        if self._running:
            logger.warning("Potentiometer handler already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_potentiometer, daemon=True)
        self._thread.start()
        logger.info("Potentiometer polling started")
    
    def stop(self):
        """Stop background polling thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        logger.info("Potentiometer polling stopped")
    
    def _poll_potentiometer(self):
        """Background thread that polls the potentiometer"""
        logger.debug("Potentiometer polling thread started")
        
        while self._running:
            try:
                # Read ADC value
                raw_value = self._read_adc_value()
                
                # Check if value changed significantly (outside deadzone)
                if abs(raw_value - self.current_value) > self.deadzone:
                    with self._lock:
                        self.current_value = raw_value
                        self.current_percentage = self._raw_to_percentage(raw_value)
                    
                    # Call registered callbacks
                    for callback in self.callbacks:
                        try:
                            callback(self.current_value, self.current_percentage)
                        except Exception as e:
                            logger.error(f"Error in potentiometer callback: {e}")
                    
                    logger.debug(f"Potentiometer: {self.current_value} ({self.current_percentage}%)")
                
                time.sleep(0.05)  # Poll every 50ms
                
            except Exception as e:
                logger.error(f"Error in potentiometer polling loop: {e}")
                break
        
        logger.debug("Potentiometer polling thread ended")
    
    def read_once(self) -> dict:
        """
        Read potentiometer value once (non-blocking)
        
        Returns:
            Dict with 'raw' and 'percentage' keys
        """
        with self._lock:
            return {
                "raw": self.current_value,
                "percentage": self.current_percentage
            }
    
    def get_percentage(self) -> int:
        """Get current volume percentage (0-100)"""
        with self._lock:
            return self.current_percentage
    
    def get_raw_value(self) -> int:
        """Get current raw ADC value (0-255)"""
        with self._lock:
            return self.current_value
    
    def cleanup(self):
        """Clean up I2C resources"""
        self.stop()
        if self.bus:
            self.bus.close()
        logger.info("Potentiometer handler cleanup complete")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass
