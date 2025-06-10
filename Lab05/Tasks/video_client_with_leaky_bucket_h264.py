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

#WIDTH, HEIGHT = 480, 270  # 270p
#WIDTH, HEIGHT = 1280, 720 # 720p
WIDTH, HEIGHT = 1920, 1080 # 1080p

LOG_DIR = "./logs"
PLOT_DIR = "./plots"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))  # Leaky Bucket server port

frame_ids_received = []
frame_ids_lost = []
latencies = []

data = b""
frame_id_size = struct.calcsize("I")
timestamp_size = struct.calcsize("d")
length_size = struct.calcsize("L")
expected_id = 0

try:
    while True:
        # Frame ID
        while len(data) < frame_id_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        frame_id = struct.unpack("I", data[:frame_id_size])[0]
        data = data[frame_id_size:]

        # Timestamp
        while len(data) < timestamp_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        timestamp = struct.unpack("d", data[:timestamp_size])[0]
        data = data[timestamp_size:]

        # Frame size
        while len(data) < length_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        size = struct.unpack("L", data[:length_size])[0]
        data = data[length_size:]

        # Frame data
        while len(data) < size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        frame_data = data[:size]
        data = data[size:]

        # Lost frames
        while expected_id < frame_id:
            frame_ids_lost.append(expected_id)
            expected_id += 1
        expected_id = frame_id + 1
        frame_ids_received.append(frame_id)

        # Decode H.264 using FFmpeg
        process = subprocess.Popen([
            'ffmpeg', '-i', 'pipe:0',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24',
            '-loglevel', 'quiet', 'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        raw_frame = process.communicate(input=frame_data)[0]

        if len(raw_frame) != WIDTH * HEIGHT * 3:
            print(f"[!] Frame decode size mismatch. Expected {WIDTH*HEIGHT*3}, got {len(raw_frame)}.")
            continue

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        cv2.imshow("H.264 Stream (Leaky Bucket)", frame)
        latency = time.time() - timestamp
        latencies.append(latency)
        print(f"Frame {frame_id} | Latency: {latency:.3f}s")

        if cv2.waitKey(1) & 0xFF == 27:
            print("[*] ESC pressed. Exiting...")
            break

except (KeyboardInterrupt, ConnectionError) as e:
    print(f"[*] Exiting: {e}")

finally:
    client_socket.close()
    cv2.destroyAllWindows()

    # Save latency data to CSV
    latency_csv = os.path.join(LOG_DIR, "latency_data_leaky_bucket_1080p.csv")
    with open(latency_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "LatencySeconds"])
        writer.writerows(zip(frame_ids_received, latencies))
    print(f"[+] Saved latency data: {latency_csv}")

    # Save summary stats to CSV
    summary_df = pd.DataFrame({
        "Scenario": ["Leaky Bucket"],
        "FramesReceived": [len(frame_ids_received)],
        "FramesLost": [len(frame_ids_lost)]
    })
    summary_csv = os.path.join(LOG_DIR, "summary_stats_leaky_bucket_1080p.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary stats: {summary_csv}")

'''
    # Latency plot
    plt.figure(figsize=(10, 4))
    plt.plot(frame_ids_received, latencies, marker='o', linestyle='-', color='blue')
    plt.xlabel("Frame ID")
    plt.ylabel("Latency (s)")
    plt.title("H.264 Frame Latency (Leaky Bucket)")
    plt.grid(True)
    plt.tight_layout()
    latency_plot_path = os.path.join(PLOT_DIR, "latency_plot_h264_leaky_bucket.png")
    plt.savefig(latency_plot_path)
    print(f"[+] Saved latency plot: {latency_plot_path}")

    # Frame loss plot
    plt.figure()
    plt.bar(["Received", "Lost"], [len(frame_ids_received), len(frame_ids_lost)], color=["green", "red"])
    plt.title("H.264 Frame Loss (Leaky Bucket)")
    plt.tight_layout()
    loss_plot_path = os.path.join(PLOT_DIR, "frame_loss_plot_h264_leaky_bucket.png")
    plt.savefig(loss_plot_path)
    print(f"[+] Saved frame loss plot: {loss_plot_path}")
    
'''
