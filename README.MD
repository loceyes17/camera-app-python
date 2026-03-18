# 🚪 Lorex Smart Doorbell Local Dashboard & NVR

A lightweight, local network web dashboard and personal Network Video Recorder (NVR) for Lorex Wi-Fi Doorbells (specifically engineered and tested for the **Lorex B241AJC 2K Wi-Fi Video Doorbell**).

## 💡 The Problem This Solves
Lorex divides its software into two ecosystems: NVRs (Desktop) and Wi-Fi Cameras (Mobile). Because the B241AJC is a standalone Wi-Fi device, the **Lorex Cloud PC software refuses to load its live video feed**, and the device has its standard web server (Port 80) disabled. 

This Python-based application bypasses the cloud and the proprietary PC software entirely. It taps directly into the camera's local RTSP video stream to provide a live, low-latency video feed with synced audio, real-time doorbell ring alerts, and local file recording directly to your PC's hard drive.

---

## ✨ Features

* **Live 2K Video & Audio:** Uses FFmpeg to convert the camera's RTSP feed into a web-friendly HLS stream, playable in any modern browser.
* **Instant Ring Alerts:** Monitors the camera's hidden metadata stream to detect physical doorbell presses (`AlarmLocal`), triggering a drop-down web alert and an audio chime.
* **Auto-Snapshots:** Automatically snaps and displays a picture of the visitor the moment the doorbell is pressed.
* **Manual Camera Controls:** Clickable web buttons to take instant high-res snapshots or toggle local MP4 video recording on and off.
* **Safe Credential Handling:** Automatically URL-encodes complex passwords (containing `$`, `!`, etc.) so the RTSP stream doesn't crash.
* **No Cloud Required:** Everything runs locally on your own network. All media is saved directly to your PC.

---

## 🛠️ Prerequisites

winget install ffmpeg

pip install flask flask-socketio Pillow ffmpeg-python


CAMERA_IP = "10.0.X.X"      # Your doorbell's local IP address
CAMERA_USER = "admin"          # Usually 'admin'
CAMERA_PASSWORD = "YourPassword!" # The device password set in the Lorex App

Before you begin, your Windows PC needs two core components:

1. **Python 3.x:** Installed and added to your system PATH.
2. **FFmpeg:** The engine that processes the video and audio. 
   * Download the latest FFmpeg Windows build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install it via Windows Terminal: `winget install ffmpeg`
   * **Crucial:** Ensure `ffmpeg` is added to your Windows Environment Variables (PATH) so Python can use it. You can test this by opening PowerShell and typing `ffmpeg -version`.

---

## 🚀 Installation & Setup

### 1. Create the Folder Structure
Create a main folder for your project and set up the following exact structure:

```text
LorexDashboard/
├── main.py
├── templates/
│   └── index.html
└── static/
    ├── hls/
    ├── recordings/
    └── snapshots/
💻 How to Run It
		Open PowerShell and navigate to your project directory:

		PowerShell
		cd path\to\LorexDashboard
		Start the Python server:

		PowerShell
		python main.py
		Look for the success messages in the console:

		🚀 Starting Video Stream...

		👂 Listening for Doorbell Ring...

		✅ Dashboard running at http://localhost:5000

		Wait about 5 to 10 seconds for FFmpeg to generate the initial video segments.

		Open your web browser and go to: http://localhost:5000

		Tip: Modern browsers block autoplaying audio. Click the speaker icon on the video player to unmute the live feed!

		📂 Where are my files saved?
		Whenever you click "Take Snapshot", "Start Recording", or when the doorbell automatically snaps a picture of a visitor, the files are saved instantly to your hard drive inside your project folder:

		Snapshots: /static/snapshots/

		Video Clips: /static/recordings/

		🔧 Troubleshooting
		"An attempt was made to access a socket in a way forbidden..."

		Cause: Port 5000 is already in use by an older version of the script that didn't close properly.

		Fix: Open PowerShell as Administrator and run:
		Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

		Video won't load / Blank Screen

		Cause: FFmpeg isn't installed properly, or the password/IP is incorrect.

		Fix: Check the PowerShell console for 401 Unauthorized errors (wrong password) or "FFmpeg is not recognized" errors (missing system PATH).

		Lorex Cloud PC Software says "Offline (Invalid User)"

		Cause: Your camera temporarily locked the admin account due to too many bad password attempts.

		Fix: Turn off the circuit breaker to your doorbell for 10 seconds to reboot it and clear the lockout cache.