
#!/usr/bin/env python3
import socket
import subprocess
import urllib.request
import urllib.error
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
RESET = "\033[0m"

REPORT = "network_report.txt"

def clear():
    os.system("clear")

def banner():
    print(C + "=" * 45)
    print("       NETWORK DOCTOR PRO v3.0")
    print("          TERMUX EDITION")
    print("=" * 45 + RESET)

def save_report(title, data):
    with open(REPORT, "a") as f:
        f.write("\n" + "=" * 45 + "\n")
        f.write(title + "\n")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write(data + "\n")

def ping_analyzer():
    host = input("Masukkan domain/IP: ").strip()
    if not host:
        return

    print(Y + "\nMemeriksa koneksi..." + RESET)

    try:
        result = subprocess.run(
            ["ping", "-c", "4", "-W", "2", host],
            capture_output=True,
            text=True,
            timeout=15
        )

        print(result.stdout)
        save_report("PING ANALYZER", result.stdout)

        if result.returncode == 0:
            print(G + "Koneksi merespons." + RESET)
        else:
            print(R + "Host tidak merespons ping." + RESET)

    except Exception as e:
        print(R + str(e) + RESET)

def port_scanner():
    host = input("IP/domain target milikmu: ").strip()
    if not host:
        return

    ports = [21, 22, 25, 53, 80, 110,
             143, 443, 445, 3306, 8080, 8443]

    print(Y + "\nMemeriksa port umum..." + RESET)
    results = []

    try:
        ip = socket.gethostbyname(host)
        print("Target:", ip)

        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)
            status = s.connect_ex((ip, port))
            s.close()

            if status == 0:
                msg = f"PORT {port}: OPEN"
                print(G + msg + RESET)
            else:
                msg = f"PORT {port}: CLOSED/FILTERED"
                print(W + msg + RESET)

            results.append(msg)

        save_report("PORT SCANNER", "\n".join(results))

    except Exception as e:
        print(R + str(e) + RESET)

def dns_lookup():
    domain = input("Masukkan domain: ").strip()

    try:
        result = socket.getaddrinfo(domain, None)
        addresses = sorted(set(x[4][0] for x in result))

        print(G + "\nDNS RESULT:" + RESET)
        for ip in addresses:
            print(C + ip + RESET)

        save_report("DNS LOOKUP", "\n".join(addresses))

    except Exception as e:
        print(R + "DNS Error: " + str(e) + RESET)

def server_health():
    url = input("URL website (https://...): ").strip()

    if not url.startswith(("http://", "https://")):
        print(R + "URL harus menggunakan http:// atau https://" + RESET)
        return

    try:
        start = time.time()

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NetworkDoctor/3.0"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            latency = (time.time() - start) * 1000

            data = (
                f"URL: {url}\n"
                f"Status: {response.status}\n"
                f"Latency: {latency:.2f} ms\n"
                f"Server: {response.headers.get('Server', 'Tidak diketahui')}\n"
                f"Content-Type: {response.headers.get('Content-Type', 'Tidak diketahui')}"
            )

            print(G + "\nSERVER HEALTH CHECK" + RESET)
            print(data)
            save_report("SERVER HEALTH", data)

    except urllib.error.HTTPError as e:
        print(Y + f"HTTP Error: {e.code}" + RESET)
        save_report("SERVER HEALTH", str(e))

    except Exception as e:
        print(R + "Server Error: " + str(e) + RESET)

def connection_analyzer():
    host = input("Masukkan domain/IP: ").strip()

    try:
        ip = socket.gethostbyname(host)
        print(C + "\nCONNECTION ANALYSIS" + RESET)
        print("Hostname :", host)
        print("IP       :", ip)

        try:
            name = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            name = "Tidak tersedia"

        print("Reverse DNS:", name)

        data = f"Host: {host}\nIP: {ip}\nReverse DNS: {name}"
        save_report("CONNECTION ANALYZER", data)

    except Exception as e:
        print(R + str(e) + RESET)

def network_info():
    print(C + "\nNETWORK INFORMATION" + RESET)

    hostname = socket.gethostname()

    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "Tidak tersedia"

    print("Device hostname:", hostname)
    print("Local IP       :", ip)

    print("\nInformasi jaringan tambahan:")

    try:
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout or "Route tidak tersedia")
    except Exception:
        print("Perintah ip tidak tersedia")

    save_report("NETWORK INFORMATION",
                f"Hostname: {hostname}\nIP: {ip}")

def live_monitor():
    url = input("URL website milikmu: ").strip()

    if not url.startswith(("http://", "https://")):
        print(R + "URL tidak valid." + RESET)
        return

    print(Y + "\nMONITORING DIMULAI (maksimal 10 pemeriksaan)" + RESET)

    logs = []

    for i in range(10):
        start = time.time()

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NetworkDoctor/3.0"}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                latency = (time.time() - start) * 1000
                msg = f"{i+1}. ONLINE | HTTP {response.status} | {latency:.2f} ms"
                print(G + msg + RESET)

        except Exception as e:
            msg = f"{i+1}. ERROR | {str(e)}"
            print(R + msg + RESET)

        logs.append(msg)

        if i < 9:
            time.sleep(2)

    save_report("LIVE MONITOR", "\n".join(logs))

def view_report():
    if os.path.exists(REPORT):
        with open(REPORT, "r") as f:
            print(f.read())
    else:
        print(Y + "Belum ada laporan." + RESET)

def main():
    while True:
        clear()
        banner()

        print("""
[1] Ping Analyzer
[2] Port Scanner
[3] DNS Lookup
[4] Server Health Check
[5] Connection Analyzer
[6] Network Information
[7] Live Server Monitor
[8] View Security Report
[9] Exit
""")

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            ping_analyzer()
        elif choice == "2":
            port_scanner()
        elif choice == "3":
            dns_lookup()
        elif choice == "4":
            server_health()
        elif choice == "5":
            connection_analyzer()
        elif choice == "6":
            network_info()
        elif choice == "7":
            live_monitor()
        elif choice == "8":
            view_report()
        elif choice == "9":
            print(G + "Terima kasih!" + RESET)
            break
        else:
            print(R + "Pilihan tidak valid." + RESET)

        input("\nTekan ENTER untuk kembali ke menu...")

if __name__ == "__main__":
    main()
