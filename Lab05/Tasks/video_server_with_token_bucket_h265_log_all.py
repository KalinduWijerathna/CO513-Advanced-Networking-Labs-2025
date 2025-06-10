import cv2
import socket
import struct
import time
import threading
import subprocess

# Token Bucket Parameters
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
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9997))  # New port for H.265
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

        # Encode frame to H.265 using FFmpeg
        encode_start_time = time.time()
        process = subprocess.Popen([
            'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f"{WIDTH}x{HEIGHT}",
            '-pix_fmt', 'bgr24', '-i', '-', '-c:v', 'libx265',
            '-preset', 'ultrafast', '-x265-params', 'log-level=error',
            '-f', 'mp4', '-movflags', 'frag_keyframe+empty_moov',
            'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        h265_bytes, _ = process.communicate(input=frame.tobytes())
        encode_end_time = time.time()

        try:
            # Send structured data:
            # [FrameID][capture_time][encode_start_time][encode_end_time][size][data]
            conn.sendall(struct.pack("I", frame_id))
            conn.sendall(struct.pack("d", capture_time))
            conn.sendall(struct.pack("d", encode_start_time))
            conn.sendall(struct.pack("d", encode_end_time))
            conn.sendall(struct.pack("L", len(h265_bytes)))
            conn.sendall(h265_bytes)

            print(f"[Frame {frame_id}] Sent | Size: {len(h265_bytes)} bytes | Encode Time: {(encode_end_time - encode_start_time):.4f}s")
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
