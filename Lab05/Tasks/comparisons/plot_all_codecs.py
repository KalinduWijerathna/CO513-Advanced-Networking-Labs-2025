import pandas as pd
import matplotlib.pyplot as plt
import os

# Set up
log_dir = "../logs"
plot_dir = "./"
os.makedirs(plot_dir, exist_ok=True)

# Parameters
resolutions = ["270p", "720p", "1080p"]
file_prefixes = ["01", "02", "03"]
codecs = ["h264", "h265", "vp9"]
colors = {"h264": "blue", "h265": "green", "vp9": "red"}

# Metrics storage
latencies = {codec: [] for codec in codecs}
cpus = {codec: [] for codec in codecs}
bandwidths = {codec: [] for codec in codecs}
loss_rates = {codec: [] for codec in codecs}

# Collect data
for codec in codecs:
    for prefix, res in zip(file_prefixes, resolutions):
        latency_file = os.path.join(log_dir, f"{prefix}_log_all_latency_{codec}_{res}.csv")
        cpu_file = os.path.join(log_dir, f"{prefix}_log_all_cpu_{codec}_{res}.csv")
        bw_file = os.path.join(log_dir, f"{prefix}_log_all_bandwidth_{codec}_{res}.csv")
        summary_file = os.path.join(log_dir, f"{prefix}_log_all_summary_stats_{codec}_{res}.csv")

        latency_df = pd.read_csv(latency_file)
        cpu_df = pd.read_csv(cpu_file)
        bw_df = pd.read_csv(bw_file)
        summary_df = pd.read_csv(summary_file)

        latencies[codec].append(latency_df["LatencySeconds"].mean())
        cpus[codec].append(cpu_df["CPU_Percent"].mean())
        bandwidths[codec].append(bw_df["BandwidthMbps"].mean())

        received = summary_df["FramesReceived"].iloc[0]
        lost = summary_df["FramesLost"].iloc[0]
        loss_rate = (lost / (received + lost)) * 100
        loss_rates[codec].append(loss_rate)

# Plotting function
def make_comparative_plot(metric_dict, ylabel, title, filename):
    plt.figure(figsize=(8, 5))
    for codec in codecs:
        plt.plot(resolutions, metric_dict[codec], marker='o', linestyle='-', color=colors[codec], label=codec.upper())
    plt.title(title)
    plt.xlabel("Resolution")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, filename))
    print(f"[+] Saved: {filename}")

# Generate plots
make_comparative_plot(latencies, "Avg Latency (s)", "Latency vs Resolution (All Codecs)", "comparative_latency_vs_resolution.png")
make_comparative_plot(cpus, "Avg CPU Usage (%)", "CPU Usage vs Resolution (All Codecs)", "comparative_cpu_vs_resolution.png")
make_comparative_plot(bandwidths, "Avg Bandwidth (Mbps)", "Bandwidth vs Resolution (All Codecs)", "comparative_bandwidth_vs_resolution.png")
make_comparative_plot(loss_rates, "Frame Loss Rate (%)", "Frame Loss vs Resolution (All Codecs)", "comparative_frameloss_vs_resolution.png")

