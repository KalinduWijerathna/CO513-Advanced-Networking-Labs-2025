import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Paths
LOG_DIR = "../logs"
PLOT_DIR = "./"
os.makedirs(PLOT_DIR, exist_ok=True)

# Resolutions to compare
res_labels = ["270p", "720p", "1080p"]

# Data containers
tcp_received_pct = []
udp_received_pct = []
tcp_lost_pct = []
udp_lost_pct = []

# Load and calculate percentages
for res in res_labels:
    tcp = pd.read_csv(os.path.join(LOG_DIR, f"summary_stats_token_bucket_{res}.csv"))
    udp = pd.read_csv(os.path.join(LOG_DIR, f"summary_stats_udp_token_bucket_{res}.csv"))

    tcp_recv, tcp_lost = tcp["FramesReceived"].values[0], tcp["FramesLost"].values[0]
    udp_recv, udp_lost = udp["FramesReceived"].values[0], udp["FramesLost"].values[0]

    tcp_total = tcp_recv + tcp_lost
    udp_total = udp_recv + udp_lost

    tcp_received_pct.append((tcp_recv / tcp_total) * 100)
    tcp_lost_pct.append((tcp_lost / tcp_total) * 100)
    udp_received_pct.append((udp_recv / udp_total) * 100)
    udp_lost_pct.append((udp_lost / udp_total) * 100)

# Prepare bar groups
group_labels = ["TCP Received", "UDP Received", "TCP Lost", "UDP Lost"]
data_groups = [tcp_received_pct, udp_received_pct, tcp_lost_pct, udp_lost_pct]

x = np.arange(len(group_labels))  # 4 groups
bar_width = 0.2
offsets = [-bar_width, 0, bar_width]  # 3 bars per group

colors = ["skyblue", "orange", "green"]
plt.figure(figsize=(10, 6))

# Plot bars
for i, res in enumerate(res_labels):
    bar_positions = x + offsets[i]
    heights = [group[i] for group in data_groups]
    plt.bar(bar_positions, heights, width=bar_width, label=res, color=colors[i])

# Axis and grid
plt.xticks(x, group_labels)
plt.xlabel("Category")
plt.ylabel("Percentage of Total Frames (%)")
plt.title("TCP vs UDP Frame Delivery (Token Bucket) - Percentage")
plt.legend(title="Resolution")
plt.grid(True, linestyle='--', alpha=0.6)
plt.ylim(0, 100)
plt.tight_layout()

# Save plot
plot_path = os.path.join(PLOT_DIR, "grouped_token_bucket_tcp_udp_percent.png")
plt.savefig(plot_path)
print(f"[+] Saved percentage plot: {plot_path}")
plt.show()
