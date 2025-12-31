#!/usr/bin/env python3
"""
TTRPG Pi - A Raspberry Pi application for TTRPG gaming
Loads a website on startup and provides an API to trigger sound effects
"""

import json
import os
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request

# Initialize Flask app
app = Flask(__name__)

# Load configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
config = {}

# Global variable to track the currently playing music process
current_music_process = None
music_lock = threading.Lock()

def load_config():
    """Load configuration from config.json"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded: {config}")
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        print("Please ensure config.json exists in the same directory as ttrpg_pi.py")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        print("Please check the syntax of config.json")
        raise

def open_website():
    """Open the configured website in a browser on startup"""
    website_url = config.get('website_url', 'https://owlbear.rodeo')
    
    # Validate URL to prevent command injection
    try:
        parsed_url = urlparse(website_url)
        if parsed_url.scheme not in ('http', 'https'):
            print(f"Warning: Invalid URL scheme in config: {website_url}")
            print("URL must start with http:// or https://")
            return
    except Exception as e:
        print(f"Warning: Invalid URL in config: {website_url} - {e}")
        return
    
    # Try to open in Chromium browser (common on Raspberry Pi)
    # Using kiosk mode for fullscreen display
    try:
        print(f"Opening website: {website_url}")
        # Try chromium-browser first (Raspberry Pi default)
        subprocess.Popen([
            'chromium-browser',
            '--kiosk',
            '--noerrdialogs',
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            website_url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        try:
            # Try google-chrome as fallback
            subprocess.Popen([
                'google-chrome',
                '--kiosk',
                '--noerrdialogs',
                '--disable-infobars',
                website_url
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            try:
                # Try firefox as last resort
                subprocess.Popen([
                    'firefox',
                    '--kiosk',
                    website_url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("Warning: Could not open browser. Please install chromium-browser, google-chrome, or firefox.")

def stop_music():
    """Stop the currently playing music"""
    global current_music_process
    with music_lock:
        if current_music_process and current_music_process.poll() is None:
            # Process is still running, terminate it
            current_music_process.terminate()
            try:
                current_music_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                current_music_process.kill()
            current_music_process = None
            return True
        current_music_process = None
        return False

def play_music(audio_file_path):
    """Play an MP3 file on loop using mpg123 or mpg321"""
    global current_music_process
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Ensure the path is absolute and safe
    audio_file_path = os.path.abspath(audio_file_path)
    
    with music_lock:
        # Stop any currently playing music (inside the lock to avoid race conditions)
        if current_music_process and current_music_process.poll() is None:
            # Process is still running, terminate it
            current_music_process.terminate()
            try:
                current_music_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                current_music_process.kill()
        
        try:
            # Try mpg123 first (recommended for Raspberry Pi) with infinite loop
            current_music_process = subprocess.Popen(
                ['mpg123', '-q', '--loop', '-1', audio_file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            try:
                # Try mpg321 as fallback with infinite loop (uses -l 0 instead of --loop -1)
                current_music_process = subprocess.Popen(
                    ['mpg321', '-q', '-l', '0', audio_file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                try:
                    # Try ffplay as another fallback with infinite loop
                    current_music_process = subprocess.Popen(
                        ['ffplay', '-nodisp', '-loglevel', 'quiet', '-loop', '0', audio_file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except FileNotFoundError:
                    raise RuntimeError("No MP3 player found. Please install mpg123, mpg321, or ffmpeg.")

@app.route('/')
def index():
    """Root endpoint - returns API information"""
    return jsonify({
        'name': 'TTRPG Pi API',
        'version': '1.0.0',
        'description': 'API for playing music on Raspberry Pi',
        'endpoints': {
            '/': 'This help message',
            '/play/<button_number>': 'Play music for button 1-8 on repeat (GET)',
            '/play': 'Play music by button number in JSON body on repeat (POST)',
            '/stop': 'Stop currently playing music (GET)',
            '/config': 'Get current configuration',
            '/health': 'Health check endpoint'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/stop', methods=['GET'])
def stop():
    """Stop currently playing music"""
    stopped = stop_music()
    if stopped:
        return jsonify({
            'status': 'stopped',
            'message': 'Music playback stopped'
        })
    else:
        return jsonify({
            'status': 'no_music',
            'message': 'No music was playing'
        })

@app.route('/config')
def get_config():
    """Return current configuration"""
    return jsonify(config)

@app.route('/play/<int:button_number>', methods=['GET'])
def play_button(button_number):
    """
    Play sound effect for a specific button (1-8)
    GET /play/<button_number>
    """
    if button_number < 1 or button_number > 8:
        return jsonify({
            'error': 'Invalid button number',
            'message': 'Button number must be between 1 and 8'
        }), 400
    
    audio_files = config.get('audio_files', {})
    audio_file_path = audio_files.get(str(button_number))
    
    if not audio_file_path:
        return jsonify({
            'error': 'Audio file not configured',
            'message': f'No audio file configured for button {button_number}'
        }), 404
    
    # Make path absolute and resolve it to prevent path traversal
    base_dir = Path(__file__).parent.resolve()
    audio_file_path = (base_dir / audio_file_path).resolve()
    
    # Ensure the resolved path is within the project directory (prevent path traversal)
    try:
        audio_file_path.relative_to(base_dir)
    except ValueError:
        return jsonify({
            'error': 'Invalid audio file path',
            'message': 'Audio file path must be within the project directory'
        }), 400
    
    if not audio_file_path.exists():
        return jsonify({
            'error': 'Audio file not found',
            'message': f'Audio file does not exist: {audio_file_path}',
            'help': 'Please add MP3 files to the audio directory. See audio/README.md for details.'
        }), 404
    
    try:
        # Play music in a separate thread to not block the API response
        threading.Thread(target=play_music, args=(str(audio_file_path),), daemon=True).start()
        
        return jsonify({
            'status': 'playing',
            'button': button_number,
            'file': str(audio_file_path.name)
        })
    except Exception as e:
        return jsonify({
            'error': 'Playback error',
            'message': str(e)
        }), 500

@app.route('/play', methods=['POST'])
def play_button_post():
    """
    Play sound effect for a specific button (1-8)
    POST /play
    Body: {"button": 1-8}
    """
    data = request.get_json()
    
    if not data or 'button' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request body must contain "button" field'
        }), 400
    
    button_number = data['button']
    
    if not isinstance(button_number, int) or button_number < 1 or button_number > 8:
        return jsonify({
            'error': 'Invalid button number',
            'message': 'Button number must be an integer between 1 and 8'
        }), 400
    
    # Reuse the GET endpoint logic
    return play_button(button_number)

def main():
    """Main entry point"""
    # Load configuration
    load_config()
    
    # Open website in browser (in a separate thread to not block the API)
    threading.Thread(target=open_website, daemon=True).start()
    
    # Start Flask API server
    # Listen on all interfaces (0.0.0.0) so it can be accessed from buttons/other devices
    print("Starting TTRPG Pi API server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
