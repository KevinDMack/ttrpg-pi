# ttrpg-pi
A solution for playing TTRPG music and managing map viewing on a Raspberry Pi

## Overview

This application runs on a Raspberry Pi (Ubuntu 22.04) and provides:
- Automatic opening of https://owlbear.rodeo (or any configured website) on startup
- A REST API to trigger playback of 8 different MP3 sound effects
- Support for physical buttons connected to the Pi to trigger sounds
- Audio output through Bluetooth speaker or wired connection

## Hardware Requirements

- Raspberry Pi (tested on Ubuntu 22.04)
- 8 buttons (optional, for physical button control)
- Bluetooth speaker or wired audio output
- Internet connection for loading the website

## Software Requirements

- Python 3.8 or higher
- Chromium browser (or Firefox/Chrome)
- MP3 player (`mpg123` recommended, or `mpg321`, or `ffmpeg`)

## Installation

### 1. Install System Dependencies

On Ubuntu 22.04 (Raspberry Pi):

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip chromium-browser mpg123
```

### 2. Clone the Repository

```bash
git clone https://github.com/KevinDMack/ttrpg-pi.git
cd ttrpg-pi
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Add Your Audio Files

Place your 8 MP3 files in the `audio/` directory with the following names:
- `sound1.mp3`
- `sound2.mp3`
- `sound3.mp3`
- `sound4.mp3`
- `sound5.mp3`
- `sound6.mp3`
- `sound7.mp3`
- `sound8.mp3`

See `audio/README.md` for more details.

### 5. Configure the Website (Optional)

Edit `config.json` to change the website URL:

```json
{
  "website_url": "https://owlbear.rodeo"
}
```

## Usage

### Running the Application

```bash
python3 ttrpg_pi.py
```

This will:
1. Open the configured website in fullscreen (kiosk mode)
2. Start the API server on `http://0.0.0.0:5000`

### API Endpoints

#### Get API Information
```bash
curl http://localhost:5000/
```

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Get Configuration
```bash
curl http://localhost:5000/config
```

#### Play Sound (GET)
```bash
curl http://localhost:5000/play/1  # Play sound 1
curl http://localhost:5000/play/2  # Play sound 2
# ... up to 8
```

#### Play Sound (POST)
```bash
curl -X POST http://localhost:5000/play \
  -H "Content-Type: application/json" \
  -d '{"button": 1}'
```

### Connecting Physical Buttons

To connect physical buttons to your Raspberry Pi:

1. Wire 8 buttons to GPIO pins (with appropriate pull-up resistors enabled in software)
2. Use the included `button_listener.py` script, or create your own
3. Example button script (requires `RPi.GPIO` or `gpiozero`):

```python
import requests
from gpiozero import Button
from signal import pause

# Define button pins (adjust based on your wiring)
# Using pull_up=True means you wire: button -> GPIO pin -> Ground
button_pins = {
    1: 2, 2: 3, 3: 4, 4: 17,
    5: 27, 6: 22, 7: 10, 8: 9
}

# Create buttons with pull-up resistors
buttons = {num: Button(pin, pull_up=True) for num, pin in button_pins.items()}

# Trigger API when button is pressed (using default parameter to capture value)
def play_sound(button_num):
    requests.get(f'http://localhost:5000/play/{button_num}')

for num, button in buttons.items():
    button.when_pressed = lambda n=num: play_sound(n)

print("Button listener started")
pause()
```

Save this as `button_listener.py` and run it alongside the main application.

## Running on Startup

To automatically start the application when your Raspberry Pi boots:

### Using systemd

1. Create a service file:

```bash
sudo nano /etc/systemd/system/ttrpg-pi.service
```

2. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=TTRPG Pi Server
After=network.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ttrpg-pi
ExecStart=/usr/bin/python3 /home/pi/ttrpg-pi/ttrpg_pi.py
Restart=on-failure
RestartSec=10
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"

[Install]
WantedBy=graphical.target
```

Note: See the included `ttrpg-pi.service` file for a ready-to-use service configuration.

3. Enable and start the service:

```bash
sudo systemctl enable ttrpg-pi.service
sudo systemctl start ttrpg-pi.service
sudo systemctl status ttrpg-pi.service
```

## Bluetooth Speaker Setup

To connect a Bluetooth speaker:

```bash
# Install Bluetooth tools
sudo apt-get install bluetooth bluez pulseaudio-module-bluetooth

# Start Bluetooth service
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# Pair your speaker using bluetoothctl
bluetoothctl
> scan on
> pair [MAC_ADDRESS]
> trust [MAC_ADDRESS]
> connect [MAC_ADDRESS]
> exit
```

## Troubleshooting

### Browser doesn't open
- Make sure `chromium-browser` is installed: `sudo apt-get install chromium-browser`
- Check if X server is running: `echo $DISPLAY` should show `:0` or similar
- Try running manually: `chromium-browser --kiosk https://owlbear.rodeo`

### Audio doesn't play
- Check if audio files exist in the `audio/` directory
- Make sure `mpg123` is installed: `sudo apt-get install mpg123`
- Test audio manually: `mpg123 audio/sound1.mp3`
- Check audio output: `amixer scontrols`

### API not accessible from other devices
- Make sure the Pi's firewall allows port 5000
- Check the Pi's IP address: `hostname -I`
- Try accessing: `http://[PI_IP_ADDRESS]:5000`

## License

See LICENSE file for details.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
