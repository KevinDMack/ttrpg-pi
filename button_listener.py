#!/usr/bin/env python3
"""
Button Listener for TTRPG Pi
Monitors GPIO pins for button presses and triggers API calls to play sounds

Requirements:
- gpiozero library: pip3 install gpiozero
- RPi.GPIO library: pip3 install RPi.GPIO

Usage:
    python3 button_listener.py

Note: Adjust the GPIO pin numbers below based on your button wiring
"""

import requests
from signal import pause

try:
    from gpiozero import Button
except ImportError:
    print("Error: gpiozero library not found")
    print("Install it with: pip3 install gpiozero RPi.GPIO")
    exit(1)

# API endpoint
API_URL = "http://localhost:5000/play"

# Define button GPIO pins (BCM numbering)
# Adjust these pin numbers based on your actual wiring
BUTTON_PINS = {
    1: 2,   # Button 1 on GPIO 2
    2: 3,   # Button 2 on GPIO 3
    3: 4,   # Button 3 on GPIO 4
    4: 17,  # Button 4 on GPIO 17
    5: 27,  # Button 5 on GPIO 27
    6: 22,  # Button 6 on GPIO 22
    7: 10,  # Button 7 on GPIO 10
    8: 9    # Button 8 on GPIO 9
}

def play_sound(button_number):
    """Trigger API to play sound for the given button number"""
    try:
        response = requests.get(f"{API_URL}/{button_number}", timeout=2)
        if response.status_code == 200:
            print(f"Button {button_number} pressed - Playing sound")
        else:
            print(f"Button {button_number} pressed - Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Button {button_number} pressed - Cannot connect to API at {API_URL}")
        print("  → Make sure ttrpg_pi.py is running: python3 ttrpg_pi.py")
    except requests.exceptions.Timeout:
        print(f"Button {button_number} pressed - Request timeout")
        print("  → API server is not responding")
    except requests.exceptions.RequestException as e:
        print(f"Button {button_number} pressed - Connection error: {e}")

def main():
    """Initialize button listeners and start monitoring"""
    print("TTRPG Pi Button Listener")
    print("=" * 40)
    print(f"Monitoring {len(BUTTON_PINS)} buttons")
    print(f"API endpoint: {API_URL}")
    print("=" * 40)
    
    # Initialize buttons and set up callbacks
    buttons = {}
    for num, pin in BUTTON_PINS.items():
        try:
            # Create button with pull-up resistor (adjust pull_up parameter if using pull-down)
            buttons[num] = Button(pin, pull_up=True, bounce_time=0.1)
            # Set callback for button press
            buttons[num].when_pressed = lambda n=num: play_sound(n)
            print(f"Button {num} initialized on GPIO {pin}")
        except Exception as e:
            print(f"Error initializing button {num} on GPIO {pin}: {e}")
    
    if not buttons:
        print("\nError: No buttons were successfully initialized")
        print("Check your wiring and GPIO pin numbers")
        return
    
    print("\n✓ Button listener started")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Keep the script running
        pause()
    except KeyboardInterrupt:
        print("\nButton listener stopped")

if __name__ == '__main__':
    main()
