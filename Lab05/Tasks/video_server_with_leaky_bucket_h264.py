import cv2
import socket
import struct
import time
import threading
import subprocess
from collections import deque

# Leaky Bucket Params
LEAK_RATE = 5  # frames per second (fixed sending rate)
leak_interval = 1.0 / LEAK_RATE

frame_queue = deque()
lock = threading.Lock()
stop_flag = False

def leak_frames(conn):
    global stop_flag
    frame_id = 0
    while not stop_flag:
        with lock:
            if frame_queue:
                frame_id, timestamp, h264_bytes = frame_queue.popleft()
            else:
                frame_id = None

        if frame_id is not None:
            try:
                conn.sendall(struct.pack("I", frame_id))
                conn.sendall(struct.pack("d", timestamp))
                conn.sendall(struct.pack("L", len(h264_bytes)) + h264_bytes)
                print(f"[Frame {frame_id}] Sent | Size: {len(h264_bytes)} bytes")
            except:
                print("[!] Connection lost.")
                stop_flag = True
                break

        time.sleep(leak_interval)

# Video and Socket Setup
cap = cv2.VideoCapture("sample_1080p.mp4")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9999))  # Different port for leaky bucket
server_socket.listen(1)
print("[+] Waiting for client...")
conn, _ = server_socket.accept()
print("[+] Client connected.")

# Start leaking thread
threading.Thread(target=leak_frames, args=(conn,), daemon=True).start()

frame_id = 0
MAX_QUEUE_SIZE = 20  # Max frames in queue to avoid memory bloat

while cap.isOpened() and not stop_flag:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode to H.264 using FFmpeg subprocess
    process = subprocess.Popen([
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f"{int(cap.get(3))}x{int(cap.get(4))}",
        '-pix_fmt', 'bgr24', '-i', '-',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',
        '-f', 'mp4', '-movflags', 'frag_keyframe+empty_moov',
        '-loglevel', 'quiet', 'pipe:1'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    h264_bytes, _ = process.communicate(input=frame.tobytes())
    timestamp = time.time()

    with lock:
        if len(frame_queue) < MAX_QUEUE_SIZE:
            frame_queue.append((frame_id, timestamp, h264_bytes))
        else:
            print(f"[!] Queue full. Dropping frame {frame_id}")

    frame_id += 1

cap.release()
stop_flag = True
conn.close()
server_socket.close()
print("[*] Server shut down.")
