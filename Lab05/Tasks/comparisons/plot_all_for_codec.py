import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

# Parse codec argument
parser = argparse.ArgumentParser(description="Generate per-frame plots across resolutions for a given codec.")
parser.add_argument("codec", choices=["h264", "h265", "vp9"], help="Codec type to analyze (e.g., h264, h265, vp9)")
args = parser.parse_args()
codec = args.codec

# Paths
log_dir = "../logs"
plot_dir = "./"
os.makedirs(plot_dir, exist_ok=True)

# Settings
resolutions = ["270p", "720p", "1080p"]
file_prefixes = ["01", "02", "03"]
colors = {"270p": "blue", "720p": "orange", "1080p": "green"}

# Containers for each metric across resolutions
latency_data = {}
cpu_data = {}
bw_data = {}
loss_data = {}

# Load data
for prefix, res in zip(file_prefixes, resolutions):
    latency_file = os.path.join(log_dir, f"{prefix}_log_all_latency_{codec}_{res}.csv")
    cpu_file = os.path.join(log_dir, f"{prefix}_log_all_cpu_{codec}_{res}.csv")
    bw_file = os.path.join(log_dir, f"{prefix}_log_all_bandwidth_{codec}_{res}.csv")
    summary_file = os.path.join(log_dir, f"{prefix}_log_all_summary_stats_{codec}_{res}.csv")

    latency_df = pd.read_csv(latency_file)
    cpu_df = pd.read_csv(cpu_file)
    bw_df = pd.read_csv(bw_file)
    summary_df = pd.read_csv(summary_file)

    latency_data[res] = latency_df
    cpu_data[res] = cpu_df
    bw_data[res] = bw_df

    # Frame loss rate is single point per resolution
    received = summary_df["FramesReceived"].iloc[0]
    lost = summary_df["FramesLost"].iloc[0]
    loss_data[res] = (lost / (received + lost)) * 100

# Helper to plot per-frame metric
def plot_metric(data_dict, y_col, ylabel, title, filename):
    plt.figure(figsize=(10, 5))
    for res in resolutions:
        df = data_dict[res]
        plt.plot(df["FrameID"], df[y_col], label=res, color=colors[res])
    plt.title(f"{title} ({codec.upper()})")
    plt.xlabel("Frame ID")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, filename))
    print(f"[+] Saved: {filename}")

# Plot latency per frame
plot_metric(latency_data, "LatencySeconds", "Latency (s)", "Latency vs Frame ID", f"frame_latency_{codec}.png")

# Plot CPU usage per frame
plot_metric(cpu_data, "CPU_Percent", "CPU Usage (%)", "CPU Usage vs Frame ID", f"frame_cpu_{codec}.png")

# Plot bandwidth per frame
plot_metric(bw_data, "BandwidthMbps", "Bandwidth (Mbps)", "Bandwidth vs Frame ID", f"frame_bandwidth_{codec}.png")

# Plot frame loss (as bar plot across resolutions)
plt.figure(figsize=(6, 4))
plt.bar(loss_data.keys(), loss_data.values(), color=[colors[res] for res in resolutions])
plt.title(f"Frame Loss Rate by Resolution ({codec.upper()})")
plt.xlabel("Resolution")
plt.ylabel("Loss Rate (%)")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"frame_loss_rate_{codec}.png"))
print(f"[+] Saved: frame_loss_rate_{codec}.png")

