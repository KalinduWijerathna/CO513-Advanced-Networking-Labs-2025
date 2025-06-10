import cv2
import socket
import struct
import time
import threading
import subprocess

# Token Bucket Params
MAX_TOKENS = 10
TOKENS_PER_FRAME = 1
TOKEN_REFILL_RATE = 5  # tokens/sec

tokens = MAX_TOKENS
lock = threading.Lock()

def refill_tokens():
    global tokens
    while True:
        with lock:
            if tokens < MAX_TOKENS:
                tokens += 1
        time.sleep(1 / TOKEN_REFILL_RATE)

threading.Thread(target=refill_tokens, daemon=True).start()

# Video and Socket Setup
cap = cv2.VideoCapture("sample_1080p.mp4")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9999))
server_socket.listen(1)
print("[+] Waiting for client...")
conn, _ = server_socket.accept()
print("[+] Client connected.")

frame_id = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[*] End of video stream.")
            break

        with lock:
            if tokens < TOKENS_PER_FRAME:
                time.sleep(0.01)
                continue
            tokens -= TOKENS_PER_FRAME

        capture_time = time.time()

        # Encode to VP9 using FFmpeg subprocess
        encode_start_time = time.time()
        process = subprocess.Popen([
            'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f"{int(cap.get(3))}x{int(cap.get(4))}",
            '-pix_fmt', 'bgr24', '-i', '-', '-c:v', 'libvpx-vp9',
            '-f', 'webm', '-deadline', 'realtime', '-cpu-used', '4',
            '-b:v', '500k', '-loglevel', 'quiet', 'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        vp9_bytes, _ = process.communicate(input=frame.tobytes())
        encode_end_time = time.time()

        try:
            # Send frame header + timestamps + data
            conn.sendall(struct.pack("I", frame_id))  # Frame ID
            conn.sendall(struct.pack("d", capture_time))  # Capture timestamp
            conn.sendall(struct.pack("d", encode_start_time))  # Encode start timestamp
            conn.sendall(struct.pack("d", encode_end_time))  # Encode end timestamp
            conn.sendall(struct.pack("L", len(vp9_bytes)) + vp9_bytes)  # Frame size + data
            print(f"[Frame {frame_id}] Sent | Size: {len(vp9_bytes)} bytes | Encode Time: {(encode_end_time - encode_start_time):.4f}s")
        except BrokenPipeError:
            print("[!] Client disconnected.")
            break

        frame_id += 1

except Exception as e:
    print(f"[!] Server error: {e}")

finally:
    cap.release()
    conn.close()
    server_socket.close()
    print("[*] Server shut down.")
