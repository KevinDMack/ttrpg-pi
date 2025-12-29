# Quick Start Guide

## 1. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip chromium-browser mpg123
pip3 install -r requirements.txt
```

## 2. Add Your Audio Files

Place your 8 MP3 files in the `audio/` directory:
```bash
# Copy your files to:
audio/sound1.mp3
audio/sound2.mp3
audio/sound3.mp3
audio/sound4.mp3
audio/sound5.mp3
audio/sound6.mp3
audio/sound7.mp3
audio/sound8.mp3
```

## 3. Run the Application

```bash
python3 ttrpg_pi.py
```

This will:
- Open https://owlbear.rodeo in fullscreen
- Start the API server on port 5000

## 4. Test the API

```bash
# Play sound 1
curl http://localhost:5000/play/1

# Play sound 5
curl http://localhost:5000/play/5

# Run full test suite
python3 test_api.py
```

## 5. Connect Buttons (Optional)

Edit `button_listener.py` to match your GPIO wiring, then run:

```bash
pip3 install gpiozero RPi.GPIO
python3 button_listener.py
```

## 6. Auto-start on Boot

```bash
# Copy service file
sudo cp ttrpg-pi.service /etc/systemd/system/

# Edit paths in the service file if needed
sudo nano /etc/systemd/system/ttrpg-pi.service

# Enable and start
sudo systemctl enable ttrpg-pi.service
sudo systemctl start ttrpg-pi.service
```

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status ttrpg-pi.service
```

### View Logs
```bash
journalctl -u ttrpg-pi.service -f
```

### Test Audio Manually
```bash
mpg123 audio/sound1.mp3
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/config` | GET | Get configuration |
| `/play/1` to `/play/8` | GET | Play sound 1-8 |
| `/play` | POST | Play sound with JSON body |

Example POST request:
```bash
curl -X POST http://localhost:5000/play \
  -H "Content-Type: application/json" \
  -d '{"button": 3}'
```
