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
import psutil

#WIDTH, HEIGHT = 480, 270 # 270p
#WIDTH, HEIGHT = 1280, 720 # 720p
WIDTH, HEIGHT = 1920, 1080 # 1080p

LOG_DIR = "./logs"
PLOT_DIR = "./plots"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9997))  # Match H.265 server port

frame_ids_received = []
frame_ids_lost = []
latencies = []
cpu_usages = []
bandwidths_mbps = []

data = b""
frame_id_size = struct.calcsize("I")
timestamp_size = struct.calcsize("d")
length_size = struct.calcsize("L")
expected_id = 0

try:
    while True:
        start_time = time.time()
        cpu_before = psutil.cpu_percent(interval=None)

        # Frame ID
        while len(data) < frame_id_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        frame_id = struct.unpack("I", data[:frame_id_size])[0]
        data = data[frame_id_size:]

        # Timestamps (capture, encode_start, encode_end)
        while len(data) < timestamp_size * 3:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        capture_time, encode_start_time, encode_end_time = struct.unpack("ddd", data[:timestamp_size * 3])
        data = data[timestamp_size * 3:]

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

        # Lost frame detection
        while expected_id < frame_id:
            frame_ids_lost.append(expected_id)
            expected_id += 1
        expected_id = frame_id + 1
        frame_ids_received.append(frame_id)

        # Decode H.265 using FFmpeg
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
        cv2.imshow("H.265 Stream", frame)

        latency = time.time() - capture_time
        cpu_after = psutil.cpu_percent(interval=None)
        cpu_usage = (cpu_before + cpu_after) / 2
        duration = time.time() - start_time
        bandwidth_mbps = (size * 8) / (duration * 1_000_000)

        latencies.append(latency)
        cpu_usages.append(cpu_usage)
        bandwidths_mbps.append(bandwidth_mbps)

        print(f"Frame {frame_id} | Latency: {latency:.3f}s | CPU: {cpu_usage:.2f}% | BW: {bandwidth_mbps:.2f} Mbps")

        if cv2.waitKey(1) & 0xFF == 27:
            print("[*] ESC pressed. Exiting...")
            break

except (KeyboardInterrupt, ConnectionError) as e:
    print(f"[*] Exiting: {e}")

finally:
    client_socket.close()
    cv2.destroyAllWindows()

    # Save latency data
    latency_csv = os.path.join(LOG_DIR, "latency_data_token_bucket_log_all_h265.csv")
    with open(latency_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "LatencySeconds"])
        writer.writerows(zip(frame_ids_received, latencies))
    print(f"[+] Saved latency data: {latency_csv}")

    # Save CPU usage data
    cpu_csv = os.path.join(LOG_DIR, "cpu_usage_log_all_h265.csv")
    with open(cpu_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "CPU_Percent"])
        writer.writerows(zip(frame_ids_received, cpu_usages))
    print(f"[+] Saved CPU usage data: {cpu_csv}")

    # Save bandwidth data
    bw_csv = os.path.join(LOG_DIR, "bandwidth_log_all_h265.csv")
    with open(bw_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "BandwidthMbps"])
        writer.writerows(zip(frame_ids_received, bandwidths_mbps))
    print(f"[+] Saved bandwidth data: {bw_csv}")

    # Summary
    summary_df = pd.DataFrame({
        "Scenario": ["Token Bucket"],
        "FramesReceived": [len(frame_ids_received)],
        "FramesLost": [len(frame_ids_lost)]
    })
    summary_csv = os.path.join(LOG_DIR, "summary_stats_token_bucket_log_all_h265.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary stats: {summary_csv}")

    # Latency plot
    plt.figure(figsize=(10, 4))
    plt.plot(frame_ids_received, latencies, marker='o', linestyle='-', color='purple')
    plt.xlabel("Frame ID")
    plt.ylabel("Latency (s)")
    plt.title("H.265 Frame Latency (Token Bucket)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "latency_plot_h265_token_bucket_log_all.png"))
    print(f"[+] Saved latency plot.")

    # Frame loss plot
    plt.figure()
    plt.bar(["Received", "Lost"], [len(frame_ids_received), len(frame_ids_lost)], color=["green", "red"])
    plt.title("H.265 Frames Received vs Lost")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "frame_loss_plot_h265_token_bucket_log_all.png"))
    print(f"[+] Saved frame loss plot.")
