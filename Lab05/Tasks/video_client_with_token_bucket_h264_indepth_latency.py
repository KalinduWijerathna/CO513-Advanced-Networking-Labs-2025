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

WIDTH, HEIGHT = 480, 270 # 270p
#WIDTH, HEIGHT = 1280, 720 # 720p
#WIDTH, HEIGHT = 1920, 1080 # 1080p

# Output directory
LOG_DIR = "./logs"
PLOT_DIR = "./plots"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9998))  # MATCH SERVER PORT

frame_ids_received = []
frame_ids_lost = []
latencies = []
encode_durations = []
network_delays = []
decode_durations = []

data = b""
frame_id_size = struct.calcsize("I")
timestamp_size = struct.calcsize("d") * 3  # 3 timestamps: original, start_encode, end_encode
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

        # Timestamps
        while len(data) < timestamp_size:
            chunk = client_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Disconnected.")
            data += chunk
        timestamps = struct.unpack("ddd", data[:timestamp_size])
        capture_time, encode_start_time, encode_end_time = timestamps
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

        # Decode start
        decode_start = time.time()
        process = subprocess.Popen([
            'ffmpeg', '-i', 'pipe:0',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24',
            '-loglevel', 'quiet', 'pipe:1'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        raw_frame = process.communicate(input=frame_data)[0]
        decode_end = time.time()

        if len(raw_frame) != WIDTH * HEIGHT * 3:
            print(f"[!] Frame decode size mismatch. Expected {WIDTH*HEIGHT*3}, got {len(raw_frame)}.")
            continue

        frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        cv2.imshow("H.264 Stream", frame)

        recv_time = time.time()
        latency = recv_time - capture_time
        encode_duration = encode_end_time - encode_start_time
        network_delay = recv_time - encode_end_time
        decode_duration = decode_end - decode_start

        latencies.append(latency)
        encode_durations.append(encode_duration)
        network_delays.append(network_delay)
        decode_durations.append(decode_duration)

        print(f"Frame {frame_id} | Total: {latency:.3f}s | Encode: {encode_duration:.3f}s | Net: {network_delay:.3f}s | Decode: {decode_duration:.3f}s")

        if cv2.waitKey(1) & 0xFF == 27:
            print("[*] ESC pressed. Exiting...")
            break

except (KeyboardInterrupt, ConnectionError) as e:
    print(f"[*] Exiting: {e}")

finally:
    client_socket.close()
    cv2.destroyAllWindows()

    # Save latency breakdown to CSV
    latency_csv = os.path.join(LOG_DIR, "latency_breakdown_h264_token_bucket_indepth.csv")
    with open(latency_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FrameID", "TotalLatency", "EncodeDuration", "NetworkDelay", "DecodeDuration"])
        for i in range(len(frame_ids_received)):
            writer.writerow([
                frame_ids_received[i],
                latencies[i],
                encode_durations[i],
                network_delays[i],
                decode_durations[i]
            ])
    print(f"[+] Saved detailed latency data: {latency_csv}")

    # Summary stats
    summary_df = pd.DataFrame({
        "Scenario": ["Token Bucket"],
        "FramesReceived": [len(frame_ids_received)],
        "FramesLost": [len(frame_ids_lost)]
    })
    summary_csv = os.path.join(LOG_DIR, "summary_stats_token_bucket_indepth.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Saved summary stats: {summary_csv}")

    # Latency plot
    plt.figure(figsize=(10, 4))
    plt.plot(frame_ids_received, latencies, label="Total Latency", color='blue')
    plt.plot(frame_ids_received, encode_durations, label="Encode Time", linestyle='--', color='green')
    plt.plot(frame_ids_received, network_delays, label="Network Delay", linestyle='--', color='orange')
    plt.plot(frame_ids_received, decode_durations, label="Decode Time", linestyle='--', color='red')
    plt.xlabel("Frame ID")
    plt.ylabel("Time (s)")
    plt.title("Latency Breakdown per Frame (H.264 Token Bucket)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    latency_plot_path = os.path.join(PLOT_DIR, "latency_breakdown_plot_h264_token_bucket_indepth.png")
    plt.savefig(latency_plot_path)
    print(f"[+] Saved latency breakdown plot: {latency_plot_path}")

    # Frame loss plot
    plt.figure()
    plt.bar(["Received", "Lost"], [len(frame_ids_received), len(frame_ids_lost)], color=["green", "red"])
    plt.title("H.264 Frame Loss (Token Bucket)")
    plt.tight_layout()
    loss_plot_path = os.path.join(PLOT_DIR, "frame_loss_plot_h264_token_bucket_indepth.png")
    plt.savefig(loss_plot_path)
    print(f"[+] Saved frame loss plot: {loss_plot_path}")
