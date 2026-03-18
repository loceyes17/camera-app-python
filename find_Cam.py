import socket
import ipaddress
import concurrent.futures
import csv
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import subprocess
import re
import os

# --- Expanded Camera & IoT Port List ---
PORTS_TO_SCAN = [80, 443, 554, 1935, 5000, 8000, 8080, 8554, 8899, 35000, 37777, 37778]

# --- Hardware MAC Address Dictionary (OUI) ---
# The first 3 octets of a MAC address identify the manufacturer.
# You can add more to this list as you discover them!
MAC_VENDORS = {
    "C0:56:E3": "Hikvision",
    "A4:14:37": "Hikvision",
    "E0:50:8B": "Dahua",
    "38:AF:29": "Dahua",
    "9C:8E:CD": "Amcrest",
    "B0:4E:26": "TP-Link / Tapo",
    "68:FF:7B": "TP-Link / Kasa",
    "2C:AA:8E": "Wyze",
    "D0:CB:E4": "Wyze",
    "B0:C5:54": "Ring",
    "44:61:32": "Ecobee",
    "B4:E6:2D": "Reolink",
    "00:40:8C": "Axis Communications"
}

def get_mac_address(ip):
    """Retrieves the MAC address of the IP from the system's ARP table."""
    try:
        # Windows and Linux/Mac have slightly different ARP commands
        if os.name == 'nt': 
            output = subprocess.check_output(['arp', '-a', ip]).decode('utf-8', errors='ignore')
        else:
            output = subprocess.check_output(['arp', '-n', ip]).decode('utf-8', errors='ignore')
            
        # Regex to find standard MAC address formats (00:11:22:33:44:55 or 00-11-22-33-44-55)
        mac_search = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', output)
        if mac_search:
            # Standardize format to uppercase with colons
            return mac_search.group(0).upper().replace('-', ':')
    except Exception:
        pass
    return "Unknown MAC"

def identify_hardware(mac):
    """Checks the MAC address against our known vendor dictionary."""
    if mac == "Unknown MAC" or not mac:
        return "Unknown Hardware"
        
    oui = mac[:8] # Grab the first 3 octets (e.g., 'C0:56:E3')
    return MAC_VENDORS.get(oui, "Unlisted Vendor")

def scan_ports(ip, ports):
    """Scans a specific IP and attempts to grab service banners."""
    open_ports_info = {}
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5) 
        
        result = sock.connect_ex((str(ip), port))
        
        if result == 0:
            banner_info = "Open (Unidentified Service)"
            try:
                sock.settimeout(1.5) 
                
                if port in [554, 8554]:
                    payload = f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\nCSeq: 1\r\n\r\n"
                else:
                    payload = f"GET / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
                    
                sock.sendall(payload.encode())
                response = sock.recv(1024).decode('utf-8', errors='ignore')
                resp_upper = response.upper()

                if "HIKVISION" in resp_upper: banner_info = "Hikvision Device"
                elif "DAHUA" in resp_upper: banner_info = "Dahua Device"
                elif "AMCREST" in resp_upper: banner_info = "Amcrest Camera"
                elif "REOLINK" in resp_upper: banner_info = "Reolink Camera"
                elif "AXIS" in resp_upper: banner_info = "Axis Communications"
                elif "LOREX" in resp_upper: banner_info = "Lorex System"
                elif "ONVIF" in resp_upper: banner_info = "ONVIF Protocol"
                elif "RTSP" in resp_upper: banner_info = "RTSP Video Stream"
                elif "SHIP 2.0" in resp_upper: banner_info = "TP-Link Tapo/Kasa Smart Device"
                else:
                    for line in response.split('\r\n'):
                        if line.lower().startswith('server:'):
                            banner_info = line.strip() 
                            break

            except Exception:
                banner_info = "Open (No banner returned)"

            open_ports_info[port] = banner_info
            
        sock.close()
        
    # If we found open ports, let's grab the MAC address to figure out the hardware
    if open_ports_info:
        mac_addr = get_mac_address(str(ip))
        hardware = identify_hardware(mac_addr)
        return str(ip), open_ports_info, mac_addr, hardware
        
    return str(ip), None, None, None

def scan_network(subnet):
    """Scans an entire subnet concurrently."""
    print(f"\n--- Starting network scan on Subnet: {subnet} ---")
    print("Scanning... this may take 20-40 seconds.\n")
    
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        print("[-] Invalid subnet format.")
        return []

    found_devices = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(scan_ports, ip, PORTS_TO_SCAN): ip for ip in network.hosts()}

        for future in concurrent.futures.as_completed(future_to_ip):
            ip, open_ports_info, mac, hardware = future.result()
            
            if open_ports_info:
                print(f"[+] Device found at {ip} [{hardware} | {mac}]:")
                for port, banner in open_ports_info.items():
                    print(f"    -> Port {port}: {banner}")
                found_devices.append((ip, open_ports_info, mac, hardware))

    return found_devices

def export_to_csv(devices):
    """Saves the scan results to a CSV file."""
    if not devices: return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"camera_scan_{timestamp}.csv"
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["IP Address", "MAC Address", "Hardware Vendor", "Port", "Service / Banner"])
            
            for ip, ports_info, mac, hardware in devices:
                for port, banner in ports_info.items():
                    writer.writerow([ip, mac, hardware, port, banner])
                    
        print(f"\n[+] Results successfully exported to: {filename}")
    except Exception as e:
        print(f"\n[-] Failed to write CSV file: {e}")

def show_summary_popup(devices):
    """Creates a GUI popup summarizing the found devices."""
    root = tk.Tk()
    root.withdraw() 
    
    if not devices:
        messagebox.showinfo("Scan Complete", "No devices with common camera ports were found.")
        return

    msg = f"Scan Complete! Found {len(devices)} device(s):\n"
    msg += "=" * 45 + "\n\n"
    
    for ip, ports_info, mac, hardware in devices:
        msg += f"--- IP: {ip} ---\n"
        msg += f"Hardware: {hardware} ({mac})\n"
        
        for port, banner in ports_info.items():
            msg += f"Port {port}: {banner}\n"
            
            # Connection hints
            if port in [80, 8080, 8000]: msg += f" -> Connect: http://{ip}:{port}\n"
            elif port == 443: msg += f" -> Connect: https://{ip}\n"
            elif port in [554, 8554]: msg += f" -> Connect: rtsp://{ip}:{port}/\n"
            
        msg += "\n"
            
    messagebox.showinfo("Scanner Results", msg)
    root.destroy()

def main():
    print("=== IP Camera & IoT Identifier ===")
    
    choice = input("Do you already know the IP address of the device? (y/n): ").strip().lower()
    results = []

    if choice == 'y':
        target_ip = input("Enter the target IP address (e.g., 192.168.1.50): ").strip()
        try:
            ipaddress.ip_address(target_ip) 
            print(f"\n--- Scanning {target_ip} ---")
            
            ip, ports_info, mac, hardware = scan_ports(target_ip, PORTS_TO_SCAN)
            
            if ports_info:
                results.append((ip, ports_info, mac, hardware))
            else:
                print(f"[-] No common camera ports found on {target_ip}.")
                
        except ValueError:
            print("[-] Invalid IP format.")

    elif choice == 'n':
        target_subnet = input("Enter your network subnet (e.g., 192.168.1.0/24): ").strip()
        results = scan_network(target_subnet)
            
    else:
        print("[-] Invalid choice. Enter 'y' or 'n'.")
        return

    if results:
        export_to_csv(results)
    show_summary_popup(results)

if __name__ == "__main__":
    main()
