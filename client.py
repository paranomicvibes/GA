# client_script.py

import os
import requests
import socketio
import time

# Get the script's current directory and file path
script_directory = os.path.dirname(os.path.abspath(__file__))
script_file_path = os.path.abspath(__file__)

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server')
    send_script_info()

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@sio.on('script_info_error')
def on_script_info_error(error):
    print(f'Script info error: {error}')

def send_script_info():
    try:
        sio.emit('script_info', {
            'directory': script_directory,
            'file_path': script_file_path
        })
    except Exception as e:
        sio.emit('script_info_error', str(e))

if __name__ == '__main__':
    server_url = 'http://10.135.60.116:8080'  # Replace with the actual server URL
    sio.connect(server_url)
    
    while True:
        time.sleep(5)  # Adjust the interval based on your needs
        send_script_info()