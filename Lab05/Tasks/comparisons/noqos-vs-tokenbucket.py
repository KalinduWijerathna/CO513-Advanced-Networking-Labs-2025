import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
LOG_DIR = "../logs"
OUTPUT_DIR = "./"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CSV Filenames
latency_files = {
    "No QoS": os.path.join(LOG_DIR, "latency_data_no_qos.csv"),
    "Token Bucket": os.path.join(LOG_DIR, "latency_data_token_bucket.csv")
}

summary_files = {
    "No QoS": os.path.join(LOG_DIR, "summary_stats_no_qos.csv"),
    "Token Bucket": os.path.join(LOG_DIR, "summary_stats_token_bucket.csv")
}

# 1. Latency comparison plot
plt.figure(figsize=(10, 5))
for label, file_path in latency_files.items():
    df = pd.read_csv(file_path)
    plt.plot(df["FrameID"], df["LatencySeconds"], label=label, marker='o', markersize=3, linewidth=1)
plt.xlabel("Frame ID")
plt.ylabel("Latency (s)")
plt.title("Latency Comparison: No QoS vs Token Bucket")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "latency_comparison_plot.png"))
print("[+] Saved latency comparison plot: ./comparisons/latency_comparison_plot.png")

# 2. Frame loss bar chart
frame_loss_data = {}
for label, file_path in summary_files.items():
    df = pd.read_csv(file_path)
    received = int(df["FramesReceived"].iloc[0])
    lost = int(df["FramesLost"].iloc[0])
    frame_loss_data[label] = {"Received": received, "Lost": lost}

labels = list(frame_loss_data.keys())
received_counts = [frame_loss_data[label]["Received"] for label in labels]
lost_counts = [frame_loss_data[label]["Lost"] for label in labels]

x = range(len(labels))
bar_width = 0.35

plt.figure(figsize=(8, 5))
plt.bar(x, received_counts, width=bar_width, label="Received", color='green')
plt.bar([i + bar_width for i in x], lost_counts, width=bar_width, label="Lost", color='red')
plt.xticks([i + bar_width / 2 for i in x], labels)
plt.ylabel("Frame Count")
plt.title("Frame Loss Comparison: No QoS vs Token Bucket")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "frame_loss_comparison_plot.png"))
print("[+] Saved frame loss comparison plot: ./comparisons/frame_loss_comparison_plot.png")

