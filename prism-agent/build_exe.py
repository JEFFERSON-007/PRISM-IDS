"""PyInstaller Automated Standalone .exe Build Script for PRISM IDS Agent."""

import os
import subprocess
import sys


def build_agent_exe() -> None:
    """Build standalone executable for PRISM IDS Agent."""
    print("=========================================================")
    print("🚀 Building PRISM IDS Agent Standalone Executable (.exe)")
    print("=========================================================")

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

    # Base PyInstaller Command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=prism-agent",
        "--onefile",
        "--clean",
        "--add-data=rules;rules",
        "--add-data=models;models",
        "--hidden-import=scapy.layers.all",
        "--hidden-import=scapy.layers.inet",
        "--hidden-import=scapy.layers.l2",
        "agent/main.py",
    ]

    print(f"[*] Executing PyInstaller command: {' '.join(cmd)}")
    result = subprocess.call(cmd)

    if result == 0:
        dist_exe = os.path.join(agent_dir, "dist", "prism-agent.exe")
        print("=========================================================")
        print(f"✅ BUILD SUCCESSFUL! Standalone Executable Created:")
        print(f"   👉 {dist_exe}")
        print("=========================================================")
        print("Copy 'prism-agent.exe' and '.env.agent' to any Windows computer to run without Python!")
    else:
        print("❌ Build failed. Please check compiler output above.")


if __name__ == "__main__":
    build_agent_exe()
