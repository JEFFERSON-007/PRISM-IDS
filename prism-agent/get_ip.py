import socket

def get_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    ip = get_ip()
    print(f"PRIMARY_HOST_IP={ip}")
    with open("host_ip.txt", "w") as f:
        f.write(ip)
