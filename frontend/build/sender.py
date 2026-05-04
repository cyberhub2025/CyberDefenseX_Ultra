import time
import requests
import os
import socket

LOG_FILE = r"C:\Users\User\Desktop\machine1\flask.log"   # same file written by app.py
RECEIVER_URL = os.getenv("RECEIVER_URL", "http://127.0.0.1:8000/receive-logs")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "30"))


def detect_source_ip():
    configured_ip = os.getenv("SOURCE_IP")
    if configured_ip:
        return configured_ip

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())


SOURCE_IP = detect_source_ip()

def send_new_logs():
    last_position = 0


    while True:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    f.seek(last_position)   # jump to last read position
                    new_logs = f.read()
                    last_position = f.tell()

                if new_logs.strip():
                    response = requests.post(
                        RECEIVER_URL,
                        data=new_logs.encode("utf-8"),
                        headers={"X-Source-IP": SOURCE_IP},
                        timeout=10,
                    )
                    print(f"📤 Sent new logs ({len(new_logs.splitlines())} lines), Response: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    send_new_logs()
