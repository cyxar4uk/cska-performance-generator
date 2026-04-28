import os
import sys
import time
import subprocess

print("Finding process on port 8000...")
result = subprocess.run(
    'netstat -ano | findstr ":8000.*LISTENING"',
    shell=True,
    capture_output=True,
    text=True
)

if result.stdout:
    lines = result.stdout.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            pid = parts[-1]
            print(f"Found PID: {pid}")
            os.system(f"taskkill /F /PID {pid}")
            print(f"Killed process {pid}")

print("Waiting for port to be released...")
time.sleep(3)

print("Starting new backend...")
subprocess.Popen(
    [sys.executable, "main.py"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
)
print("Backend restarted!")
time.sleep(2)

# Проверка
import requests
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Backend status: {r.json()}")
except Exception as e:
    print(f"Backend check failed: {e}")

