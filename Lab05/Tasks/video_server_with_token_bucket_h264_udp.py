# h264_server_udp.py
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

# Setup
cap = cv2.VideoCapture("sample_720p.mp4")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_addr = ("localhost", 9999)  # Default destination

frame_id = 0

print("[+] UDP Streaming started...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    with lock:
        if tokens < TOKENS_PER_FRAME:
            frame_id += 1
            time.sleep(0.01)
            continue
        tokens -= TOKENS_PER_FRAME

    # Encode to H.264
    process = subprocess.Popen([
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f"{int(cap.get(3))}x{int(cap.get(4))}",
        '-pix_fmt', 'bgr24', '-i', '-', '-c:v', 'libx264',
        '-preset', 'ultrafast', '-tune', 'zerolatency',
        '-f', 'mp4', '-movflags', 'frag_keyframe+empty_moov',
        '-loglevel', 'quiet', 'pipe:1'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    h264_bytes, _ = process.communicate(input=frame.tobytes())
    timestamp = time.time()

    # Packet format: [frame_id][timestamp][length][data]
    header = struct.pack("!IdI", frame_id, timestamp, len(h264_bytes))
    packet = header + h264_bytes


    try:
        server_socket.sendto(packet, client_addr)
        print(f"[Frame {frame_id}] Sent | Size: {len(h264_bytes)} bytes")
    except Exception as e:
        print("[!] Send error:", e)

    frame_id += 1

cap.release()
server_socket.close()
print("[*] UDP Server shut down.")
