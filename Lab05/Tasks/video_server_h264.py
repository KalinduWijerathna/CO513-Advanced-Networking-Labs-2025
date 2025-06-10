# h264_server_no_qos.py
import cv2
import socket
import struct
import time
import subprocess

# Video and Socket Setup
cap = cv2.VideoCapture("sample_270p.mp4")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 9996))  # H.264 port
server_socket.listen(1)
print("[+] Waiting for client...")
conn, _ = server_socket.accept()
print("[+] Client connected.")

frame_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Encode to H.264 using FFmpeg subprocess
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

    try:
        conn.sendall(struct.pack("I", frame_id))
        conn.sendall(struct.pack("d", timestamp))
        conn.sendall(struct.pack("L", len(h264_bytes)) + h264_bytes)
        print(f"[Frame {frame_id}] Sent | Size: {len(h264_bytes)} bytes")
    except:
        print("[!] Connection lost.")
        break

    frame_id += 1

cap.release()
conn.close()
print("[*] Server shut down.")
