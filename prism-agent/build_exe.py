"""PyInstaller Automated Standalone .exe Build Script for PRISM IDS Agent."""

import os
import socket
import subprocess
import sys

# Ensure PIL/Raw icon generation script runs first
try:
    from create_icon import create_prism_icon
    icon_path = create_prism_icon("prism_icon.ico")
except Exception as err:
    print(f"[*] Icon creation warning: {err}")
    icon_path = None


def get_primary_ip() -> str:
    """Detect primary IPv4 address of this Central Server host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def build_agent_exe() -> None:
    """Build standalone executable for PRISM IDS Agent configured for this Central Server."""
    print("=========================================================")
    print("🚀 Building PRISM IDS Agent Optimized Standalone (.exe)")
    print("=========================================================")

    # Force kill any active background instances to unlock destination files
    if sys.platform == "win32":
        try:
            subprocess.call(["taskkill", "/F", "/IM", "prism-agent.exe", "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call(["taskkill", "/F", "/IM", "prism-agent-sensor.exe", "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    central_ip = get_primary_ip()
    central_server_url = "http://127.0.0.1:8000"
    print(f"[*] Auto-Detected Central Server Host IP: {central_ip}")
    print(f"[*] Pre-configuring executable to connect to: {central_server_url}")

    # Install PyInstaller if missing
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    agent_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(agent_dir)

    # Ensure required asset directories exist
    rules_dir = os.path.join(agent_dir, "rules")
    models_dir = os.path.join(agent_dir, "models")
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    # Automatically write/update .env.agent with detected Central Server URL
    env_agent_path = os.path.join(agent_dir, ".env.agent")
    env_content = f"""# PRISM IDS Agent Sensor Configuration
AGENT_NAME="remote-agent-sensor"

# Default Server URL
SERVER_URL="{central_server_url}"

HEARTBEAT_INTERVAL=15
RECONNECT_INTERVAL=5
HTTP_TIMEOUT=10.0

CREDENTIALS_FILE=".agent_credentials.json"

LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_DIR="logs"
DEBUG=true
TIMEZONE="UTC"
"""
    with open(env_agent_path, "w", encoding="utf-8") as f:
        f.write(env_content)

    print(f"[*] Updated .env.agent with SERVER_URL=\"{central_server_url}\"")

    # Base PyInstaller Command bundling rules, models, icon, and .env.agent into executable
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=prism_ids_sensor",
        "--onefile",
        "--clean",
        "--add-data=rules;rules",
        "--add-data=models;models",
        "--add-data=.env.agent;.",
        "--hidden-import=concurrent.futures",
        "--hidden-import=asyncio",
        "--hidden-import=scapy.all",
        "--hidden-import=scapy.layers.all",
        "--hidden-import=scapy.layers.inet",
        "--hidden-import=scapy.layers.l2",
        "--hidden-import=sklearn.ensemble._forest",
        "--hidden-import=joblib",
        "--hidden-import=structlog",
        "--hidden-import=pydantic",
        "--hidden-import=psutil",
    ]

    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")

    cmd.append("agent/main.py")

    print(f"[*] Executing PyInstaller command: {' '.join(cmd)}")
    result = subprocess.call(cmd)

    if result == 0:
        dist_exe = os.path.join(agent_dir, "dist", "prism_ids_sensor.exe")
        print("=========================================================")
        print(f"✅ BUILD SUCCESSFUL! Standalone Executable Created:")
        print(f"   👉 {dist_exe}")
        print(f"   🎯 Pre-configured Central Server URL: {central_server_url}")
        print("=========================================================")
        print("Features Enabled:")
        print("  • Custom PRISM Security Shield Icon (.ico)")
        print("  • Automatic Background Daemon & Startup App Registration")
        print("  • Multithreaded Scapy Engine & Connection Pool")
        print("=========================================================")
    else:
        print("❌ Build failed. Please check compiler output above.")


if __name__ == "__main__":
    build_agent_exe()
