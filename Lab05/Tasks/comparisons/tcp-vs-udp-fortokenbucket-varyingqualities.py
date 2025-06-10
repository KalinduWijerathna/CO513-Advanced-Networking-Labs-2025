import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# File paths
LOG_DIR = "../logs"
PLOT_DIR = "./"
os.makedirs(PLOT_DIR, exist_ok=True)

# CSV files
files = {
    "TCP_270p": "summary_stats_token_bucket_270p.csv",
    "TCP_720p": "summary_stats_token_bucket_720p.csv",
    "TCP_1080p": "summary_stats_token_bucket_1080p.csv",
    "UDP_270p": "summary_stats_udp_token_bucket_270p.csv",
    "UDP_720p": "summary_stats_udp_token_bucket_720p.csv",
    "UDP_1080p": "summary_stats_udp_token_bucket_1080p.csv"
}

# Initialize data
res_labels = ["270p", "720p", "1080p"]
tcp_received = []
udp_received = []
tcp_lost = []
udp_lost = []

# Populate the data arrays
for res in res_labels:
    tcp_df = pd.read_csv(os.path.join(LOG_DIR, f"summary_stats_token_bucket_{res}.csv"))
    udp_df = pd.read_csv(os.path.join(LOG_DIR, f"summary_stats_udp_token_bucket_{res}.csv"))
    tcp_received.append(tcp_df["FramesReceived"].values[0])
    udp_received.append(udp_df["FramesReceived"].values[0])
    tcp_lost.append(tcp_df["FramesLost"].values[0])
    udp_lost.append(udp_df["FramesLost"].values[0])

# Plot setup
group_labels = ["TCP Received", "UDP Received", "TCP Lost", "UDP Lost"]
data_groups = [tcp_received, udp_received, tcp_lost, udp_lost]

x = np.arange(len(group_labels))  # 4 groups
bar_width = 0.2
offsets = [-bar_width, 0, bar_width]  # for 3 resolutions per group

plt.figure(figsize=(10, 6))

# Colors per resolution
colors = ["skyblue", "orange", "green"]

# Plot bars
for i, res_label in enumerate(res_labels):
    bar_positions = x + offsets[i]
    heights = [group[i] for group in data_groups]
    plt.bar(bar_positions, heights, width=bar_width, label=res_label, color=colors[i])

# Labels and grid
plt.xticks(x, group_labels)
plt.xlabel("Category")
plt.ylabel("Frame Count")
plt.title("TCP vs UDP Frame Delivery (Token Bucket QoS)")
plt.legend(title="Resolution")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Save plot
output_path = os.path.join(PLOT_DIR, "grouped_token_bucket_tcp_udp_by_type.png")
plt.savefig(output_path)
print(f"[+] Saved grouped plot: {output_path}")

