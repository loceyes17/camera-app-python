import socket
from datetime import datetime

# Camera configuration
TARGET_IP = "enter cameras IP"
# Common ports for Lorex/ONVIF devices:
# 80 (HTTP), 554 (RTSP), 8000/8554 (Alt RTSP), 35000 (Lorex Client)
PORTS_TO_SCAN = [80, 554, 888, 8000, 8080, 8554, 35000, 37777]

def scan_ports(ip, ports):
    print(f"--- Starting scan on {ip} ---")
    print(f"Time started: {datetime.now()}\n")
    
    open_ports = []
    
    for port in ports:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a short timeout for faster scanning
        sock.settimeout(1.0)
        
        # Attempt to connect to the port
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            print(f"[+] Port {port}: OPEN")
            open_ports.append(port)
        else:
            print(f"[-] Port {port}: Closed/Filtered")
            
        sock.close()
        
    print(f"\n--- Scan Complete ---")
    return open_ports

if __name__ == "__main__":
    found_ports = scan_ports(TARGET_IP, PORTS_TO_SCAN)
    if not found_ports:
        print("No common ports were found open. Ensure the doorbell is powered on and connected to the same network.")
