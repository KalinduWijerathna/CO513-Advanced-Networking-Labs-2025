# h264_client_udp.py
import socket
import struct
import time
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import cv2
import csv
import pandas as pd
import os

#WIDTH, HEIGHT = 480, 270 # 270p
WIDTH, HEIGHT = 1280, 720 # 720p
# WIDTH, HEIGHT = 1920, 1080 # 1080p

# Output dirs
LOG_DIR = "./logs"
PLOT_DIR = "./plots"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('localhost', 9999))

frame_ids_received = []
frame_ids_lost = []
latencies = []

expected_id = 0

try:
    while True:
        packet, _ = client_socket.recvfrom(65536)

        if len(packet) < struct.calcsize("IdL"):
            print("[!] Packet too small.")
            continue

        frame_id, timestamp, size = struct.unpack("!IdI", packet[:16])
        h264_data = packet[16:]

        if len(h264_data) != size:
            print(f"[!] Mismatched size: expected {size}, got {len(h264_data)}")
            continue

        # Track lost frames
        while expected_id < frame_id:
            frame_ids_lost.append(expected_id)
            expected_id += 1
        expected_id = frame_id + 1
        frame_ids_received.append(frame_id)

        # Decode H.264
        process = subprocess.Popen([
            'ffmpeg', '-i', 'pipe:0',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24',
            '-loglevel', 'quiet', 'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        raw_frame = process.communicate(input=h264_data)[0]

        if len(raw_frame) != WIDTH * HEIGHT * 3:
            print(f"[!] Decode error. Expected {WIDTH*HEIGHT*3}, got {len(raw_frame)}.")
            continue

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        cv2.imshow("H.264 UDP Stream", frame)
        latency = time.time() - timestamp
        latencies.append(latency)
        print(f"Frame {frame_id} | Latency: {latency:.3f}s")

        if cv2.waitKey(1) & 0xFF == 27:
            print("[*] ESC pressed.")
            break

except (KeyboardInterrupt, Exception) as e:
    print("[*] Exiting:", e)

finally:
    client_socket.close()
    cv2.destroyAllWindows()

    # CSV Logging
    latency_csv = os.path.join(LOG_DIR, "latency_data_udp_token_bucket.csv")
    with open(latency_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "LatencySeconds"])
        writer.writerows(zip(frame_ids_received, latencies))
    print(f"[+] Saved latency data: {latency_csv}")

    summary_df = pd.DataFrame({
        "Scenario": ["UDP Token Bucket"],
        "FramesReceived": [len(frame_ids_received)],
        "FramesLost": [len(frame_ids_lost)]
    })
    summary_csv = os.path.join(LOG_DIR, "summary_stats_udp_token_bucket.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary stats: {summary_csv}")

'''
    # Plotting
    plt.figure(figsize=(10, 4))
    plt.plot(frame_ids_received, latencies, marker='o', linestyle='-', color='blue')
    plt.xlabel("Frame ID")
    plt.ylabel("Latency (s)")
    plt.title("H.264 UDP Frame Latency (Token Bucket)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "latency_plot_udp_token_bucket.png"))
    print("[+] Saved latency plot.")

    plt.figure()
    plt.bar(["Received", "Lost"], [len(frame_ids_received), len(frame_ids_lost)], color=["green", "red"])
    plt.title("H.264 UDP Frame Loss (Token Bucket)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "frame_loss_plot_udp_token_bucket.png"))
    print("[+] Saved frame loss plot.")
'''
