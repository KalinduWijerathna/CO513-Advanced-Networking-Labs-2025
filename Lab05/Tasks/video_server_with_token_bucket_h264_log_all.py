# h264_server.py
import cv2
import socket
import struct
import time
import threading
import subprocess

# Token Bucket QoS Configuration
MAX_TOKENS = 10               # Max capacity of the bucket
TOKENS_PER_FRAME = 1          # Tokens required to send one frame
TOKEN_REFILL_RATE = 5         # Tokens added per second

tokens = MAX_TOKENS
lock = threading.Lock()

def refill_tokens():
    global tokens
    while True:
        with lock:
            if tokens < MAX_TOKENS:
                tokens += 1
        time.sleep(1 / TOKEN_REFILL_RATE)

# Start token refill thread
threading.Thread(target=refill_tokens, daemon=True).start()

# Video and Socket Setup
cap = cv2.VideoCapture("sample_1080p.mp4")
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9998))  # MATCH PORT WITH CLIENT
server_socket.listen(1)
print("[+] Waiting for client to connect...")
conn, _ = server_socket.accept()
print("[+] Client connected!")

frame_id = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[*] End of video stream.")
            break

        # Token Bucket QoS enforcement
        with lock:
            if tokens < TOKENS_PER_FRAME:
                time.sleep(0.01)
                continue
            tokens -= TOKENS_PER_FRAME

        # Timestamp and encode frame
        capture_time = time.time()

        # Start FFmpeg to encode to H.264
        encode_start_time = time.time()
        process = subprocess.Popen([
            'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f"{WIDTH}x{HEIGHT}",
            '-pix_fmt', 'bgr24', '-i', '-', '-c:v', 'libx264',
            '-preset', 'ultrafast', '-tune', 'zerolatency',
            '-f', 'mp4', '-movflags', 'frag_keyframe+empty_moov',
            '-loglevel', 'quiet', 'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        h264_bytes, _ = process.communicate(input=frame.tobytes())
        encode_end_time = time.time()

        # Frame send: [ID][capture][encode_start][encode_end][size][data]
        try:
            conn.sendall(struct.pack("I", frame_id))              # Frame ID
            conn.sendall(struct.pack("d", capture_time))          # Time captured
            conn.sendall(struct.pack("d", encode_start_time))     # Time encode started
            conn.sendall(struct.pack("d", encode_end_time))       # Time encode ended
            conn.sendall(struct.pack("L", len(h264_bytes)))       # Payload size
            conn.sendall(h264_bytes)                              # H.264 bytes

            print(f"[Frame {frame_id}] Sent | Size: {len(h264_bytes)} bytes | Encode Time: {(encode_end_time - encode_start_time):.4f}s")
            frame_id += 1

        except BrokenPipeError:
            print("[!] Client disconnected.")
            break

except Exception as e:
    print(f"[!] Server error: {e}")

finally:
    cap.release()
    conn.close()
    server_socket.close()
    print("[*] Server shut down.")
