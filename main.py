import os
import subprocess
import threading
import shutil
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- CAMERA CONFIGURATION ---
CAMERA_IP = "your IP to the camera"
CAMERA_USER = "your username"
CAMERA_PASSWORD = "Your password"
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/cam/realmonitor?channel=1&subtype=1" #this is the port it uses and protocal#

# --- FOLDERS SETUP ---
HLS_FOLDER = os.path.join('static', 'hls')
SNAP_FOLDER = os.path.join('static', 'snapshots')
REC_FOLDER = os.path.join('static', 'recordings')

for folder in [SNAP_FOLDER, REC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def prepare_hls_folder():
    if os.path.exists(HLS_FOLDER):
        shutil.rmtree(HLS_FOLDER)
    os.makedirs(HLS_FOLDER)

# Global variable to hold our recording leash
recording_process = None

# --- FFmpeg TASKS ---
def start_hls_stream():
    prepare_hls_folder()
    print("🚀 Starting Video Stream...")
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error',
        '-rtsp_transport', 'tcp', '-i', RTSP_URL,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
        '-f', 'hls', '-hls_time', '2', '-hls_list_size', '5',
        '-hls_flags', 'delete_segments',
        os.path.join(HLS_FOLDER, 'stream.m3u8')
    ]
    subprocess.run(cmd)

def take_snapshot(prefix="manual"):
    filename = f"{prefix}_{int(time.time())}.jpg"
    filepath = os.path.join(SNAP_FOLDER, filename)
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error',
        '-rtsp_transport', 'tcp', '-i', RTSP_URL,
        '-vframes', '1', '-q:v', '2', filepath
    ]
    subprocess.run(cmd)
    return f"/static/snapshots/{filename}"

def listen_for_ring():
    print("👂 Listening for Doorbell Ring...")
    cmd = ['ffmpeg', '-rtsp_transport', 'tcp', '-i', RTSP_URL, '-f', 'null', '-']
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
    
    for line in proc.stderr:
        if "AlarmLocal" in line or "VideoMotion" in line:
            print("🔔 DOORBELL RING DETECTED!")
            snap_url = take_snapshot(prefix="auto")
            socketio.emit('doorbell_ring', {
                'time': datetime.now().strftime('%H:%M:%S'),
                'msg': "Someone is at the door!",
                'image': snap_url
            })
            time.sleep(5) 

# --- WEB ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/snapshot')
def api_snapshot():
    img_path = take_snapshot()
    return jsonify({"status": "success", "file": img_path})

# NEW: Start and Stop Recording Routes
@app.route('/api/record/<action>')
def api_record(action):
    global recording_process
    
    if action == 'start':
        if recording_process is None or recording_process.poll() is not None:
            filename = f"clip_{int(time.time())}.mp4"
            filepath = os.path.join(REC_FOLDER, filename)
            cmd = [
                'ffmpeg', '-hide_banner', '-loglevel', 'error',
                '-rtsp_transport', 'tcp', '-i', RTSP_URL,
                '-c:v', 'copy', '-c:a', 'aac', filepath
            ]
            # Popen starts it in the background but lets us keep control
            recording_process = subprocess.Popen(cmd)
            return jsonify({"status": "started", "file": filename})
        return jsonify({"status": "error", "message": "Already recording!"})
        
    elif action == 'stop':
        if recording_process and recording_process.poll() is None:
            recording_process.terminate()  # Gently tell FFmpeg to stop and save the file
            recording_process.wait()       # Wait for it to finish saving
            recording_process = None
            return jsonify({"status": "stopped"})
        return jsonify({"status": "error", "message": "Not currently recording."})

if __name__ == '__main__':
    threading.Thread(target=start_hls_stream, daemon=True).start()
    threading.Thread(target=listen_for_ring, daemon=True).start()
    
    print(f"✅ Dashboard running at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)