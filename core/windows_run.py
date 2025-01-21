import os
import sys
import subprocess
import socket
import psutil
from pathlib import Path
from dotenv import load_dotenv

#檢查指定端口是否被使用
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except socket.error:
            return True

#檢查指定進程是否在運行
def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

#啟動 PocketBase 服務
def start_pocketbase():
    try:
        # 檢查 PocketBase 是否已在運行
        if is_process_running('pocketbase'):
            print("PocketBase is already running.")
            return True

        # 檢查端口是否被佔用
        if is_port_in_use(8090):
            print("Port 8090 is already in use.")
            return False

        # 構建 PocketBase 路徑
        current_dir = Path(__file__).parent
        pb_path = current_dir.parent / 'pb' / 'pocketbase.exe'  # Windows 使用 .exe
        
        if not pb_path.exists():
            print(f"PocketBase executable not found at: {pb_path}")
            return False

        # 啟動 PocketBase
        print("Starting PocketBase...")
        subprocess.Popen([
            str(pb_path),
            'serve',
            '--http=127.0.0.1:8090'
        ], 
        creationflags=subprocess.CREATE_NEW_CONSOLE)  # Windows 特定標誌
        return True

    except Exception as e:
        print(f"Error starting PocketBase: {e}")
        return False

def main():
    # 載入環境變數
    env_path = Path(__file__).parent / 'windows.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found")

    # 啟動 PocketBase
    if start_pocketbase():
        # 運行 Python 處理腳本
        try:
            process_script = Path(__file__).parent / 'windows_general_process.py'
            if process_script.exists():
                subprocess.run([sys.executable, str(process_script)], check=True)
            else:
                print(f"Error: general_process.py not found at: {process_script}")
        except subprocess.CalledProcessError as e:
            print(f"Error running general_process.py: {e}")
    else:
        print("Failed to start services")

if __name__ == '__main__':
    main()