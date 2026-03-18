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

Before you begin, your Windows PC needs two core components:

1. **Python 3.x:** Installed and added to your system PATH.
2. **FFmpeg:** The engine that processes the video and audio. 
   * Download the latest FFmpeg Windows build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or install it via Windows Terminal: 
     ```powershell
     winget install ffmpeg
     ```
   * **Crucial:** Ensure `ffmpeg` is added to your Windows Environment Variables (PATH) so Python can use it. You can test this by opening PowerShell and typing `ffmpeg -version`.

---

## 🚀 Installation & Setup

### 1. Clone or Download the Project
Ensure you have the following folder structure:

```text
camera-app-python/
├── main.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/         <-- (Auto-generated on first run)
    ├── hls/
    ├── recordings/
    └── snapshots/