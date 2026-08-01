"""PyInstaller Automated Standalone .exe Build Script for PRISM IDS Agent."""

import os
import socket
import subprocess
import sys


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
    print("🚀 Building PRISM IDS Agent Standalone Executable (.exe)")
    print("=========================================================")

    central_ip = get_primary_ip()
    central_server_url = f"http://{central_ip}:8000"
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

# Pre-configured to point automatically to your Central Server IP ({central_ip})
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

    # Base PyInstaller Command with Multithreading & Hidden Imports Optimization
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=prism-agent",
        "--onefile",
        "--clean",
        "--add-data=rules;rules",
        "--add-data=models;models",
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
        "agent/main.py",
    ]

    print(f"[*] Executing PyInstaller command: {' '.join(cmd)}")
    result = subprocess.call(cmd)

    if result == 0:
        dist_exe = os.path.join(agent_dir, "dist", "prism-agent.exe")
        print("=========================================================")
        print(f"✅ BUILD SUCCESSFUL! Standalone Executable Created:")
        print(f"   👉 {dist_exe}")
        print(f"   🎯 Pre-configured Central Server URL: {central_server_url}")
        print("=========================================================")
        print("Copy 'prism-agent.exe' and '.env.agent' to ANY computer. It will connect back to your system automatically!")
    else:
        print("❌ Build failed. Please check compiler output above.")


if __name__ == "__main__":
    build_agent_exe()
