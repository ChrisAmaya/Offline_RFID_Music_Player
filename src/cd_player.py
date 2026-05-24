"""
CD Player module for Offline RFID Music Player
Provides interface to detect and play audio from USB CD modules connected via USB
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class CDDevice:
    """Represents a CD/DVD device"""
    device_path: str
    device_name: str
    is_mounted: bool = False


class CDPlayer:
    """
    CD player interface using mpv, mplayer, or cdparanoia
    
    Usage:
        player = CDPlayer('/dev/sr0')
        player.play()  # Play from beginning
        player.stop()
        player.is_playing()
    """
    
    def __init__(self, device_path: str = '/dev/sr0'):
        """
        Initialize CD player
        
        Args:
            device_path: Path to CD device (e.g., '/dev/sr0', '/dev/sr1')
        """
        self.device_path = device_path
        self.process = None
        self.backend = None
        self._detect_backend()
        
    def _detect_backend(self) -> str:
        """Detect available CD playback backend"""
        backends = [
            ('mpv', self._play_with_mpv),
            ('mplayer', self._play_with_mplayer),
            ('cdparanoia', self._play_with_cdparanoia),
        ]
        
        for name, _ in backends:
            if self._command_exists(name):
                self.backend = name
                return name
        
        raise RuntimeError(
            "No CD playback backend found. Install: mpv, mplayer, or cdparanoia"
        )
    
    @staticmethod
    def _command_exists(command: str) -> bool:
        """Check if a command exists in PATH"""
        result = subprocess.run(
            ['which', command],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def device_exists(self) -> bool:
        """Check if CD device exists"""
        return os.path.exists(self.device_path)
    
    def play(self) -> bool:
        """
        Play CD from beginning
        
        Returns:
            True if playback started successfully, False otherwise
        """
        if not self.device_exists():
            print(f"Error: Device {self.device_path} not found")
            return False
        
        try:
            if self.backend == 'mpv':
                return self._play_with_mpv()
            elif self.backend == 'mplayer':
                return self._play_with_mplayer()
            elif self.backend == 'cdparanoia':
                return self._play_with_cdparanoia()
        except Exception as e:
            print(f"Error starting playback: {e}")
            return False
        
        return False
    
    def _play_with_mpv(self) -> bool:
        """Play using mpv"""
        try:
            self.process = subprocess.Popen(
                ['mpv', f'cdda://{self.device_path}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except FileNotFoundError:
            return False
    
    def _play_with_mplayer(self) -> bool:
        """Play using mplayer"""
        try:
            self.process = subprocess.Popen(
                ['mplayer', f'cdda://{self.device_path}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except FileNotFoundError:
            return False
    
    def _play_with_cdparanoia(self) -> bool:
        """Extract and play using cdparanoia + mpv/aplay"""
        try:
            # Extract first track to temporary file
            output_file = '/tmp/cd_track.wav'
            result = subprocess.run(
                ['cdparanoia', '-d', self.device_path, '1', output_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"cdparanoia extraction failed: {result.stderr}")
                return False
            
            # Play extracted file
            if self._command_exists('mpv'):
                self.process = subprocess.Popen(
                    ['mpv', output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif self._command_exists('aplay'):
                self.process = subprocess.Popen(
                    ['aplay', output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                print("No playback tool found to play extracted CD audio")
                return False
            
            return True
        except FileNotFoundError:
            return False
    
    def stop(self) -> bool:
        """Stop playback"""
        if self.process is None:
            return False
        
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            return True
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process = None
            return True
    
    def is_playing(self) -> bool:
        """Check if CD is currently playing"""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def get_status(self) -> dict:
        """Get current status"""
        return {
            'device': self.device_path,
            'exists': self.device_exists(),
            'playing': self.is_playing(),
            'backend': self.backend
        }


def detect_cd_devices() -> list[CDDevice]:
    """
    Detect available CD/DVD devices
    
    Returns:
        List of CDDevice objects found
    """
    devices = []
    
    # Common device paths
    device_patterns = [
        '/dev/sr0', '/dev/sr1', '/dev/sr2',
        '/dev/cdrom', '/dev/cdrom0', '/dev/cdrom1',
        '/dev/dvd', '/dev/dvd0', '/dev/dvd1'
    ]
    
    for device_path in device_patterns:
        if os.path.exists(device_path):
            # Get device name from symlinks
            try:
                if os.path.islink(device_path):
                    target = os.readlink(device_path)
                    device_name = os.path.basename(target)
                else:
                    device_name = os.path.basename(device_path)
            except:
                device_name = os.path.basename(device_path)
            
            # Check if mounted
            is_mounted = False
            try:
                result = subprocess.run(
                    ['mount'],
                    capture_output=True,
                    text=True
                )
                is_mounted = device_path in result.stdout
            except:
                pass
            
            devices.append(CDDevice(
                device_path=device_path,
                device_name=device_name,
                is_mounted=is_mounted
            ))
    
    return devices


if __name__ == '__main__':
    # Quick test
    print("Available CD devices:")
    devices = detect_cd_devices()
    for device in devices:
        print(f"  {device.device_path} ({device.device_name}) - Mounted: {device.is_mounted}")
    
    if devices:
        print(f"\nTesting CD player with {devices[0].device_path}...")
        player = CDPlayer(devices[0].device_path)
        print(f"Status: {player.get_status()}")
    else:
        print("\nNo CD devices found. Connect USB CD module and try again.")
