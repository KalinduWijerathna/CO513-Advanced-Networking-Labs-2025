import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
LOG_DIR = "../logs"
PLOT_DIR = "./"
os.makedirs(PLOT_DIR, exist_ok=True)

# Load latency CSVs
tcp_latency_path = os.path.join(LOG_DIR, "latency_data_token_bucket.csv")
udp_latency_path = os.path.join(LOG_DIR, "latency_data_udp_token_bucket.csv")

df_tcp_latency = pd.read_csv(tcp_latency_path)
df_udp_latency = pd.read_csv(udp_latency_path)

# Load summary stats
tcp_summary = pd.read_csv(os.path.join(LOG_DIR, "summary_stats_token_bucket.csv"))
udp_summary = pd.read_csv(os.path.join(LOG_DIR, "summary_stats_udp_token_bucket.csv"))

# -------- Latency Plot --------
plt.figure(figsize=(10, 4))
plt.plot(df_tcp_latency["FrameID"], df_tcp_latency["LatencySeconds"], label="TCP (Token Bucket)", color="blue")
plt.plot(df_udp_latency["FrameID"], df_udp_latency["LatencySeconds"], label="UDP (Token Bucket)", color="orange")
plt.xlabel("Frame ID")
plt.ylabel("Latency (s)")
plt.title("Latency Comparison: TCP vs UDP (Token Bucket)")
plt.legend()
plt.grid(True)
plt.tight_layout()
latency_plot_path = os.path.join(PLOT_DIR, "latency_comparison_token_bucket_tcp_vs_udp.png")
plt.savefig(latency_plot_path)
print(f"[+] Saved latency comparison plot: {latency_plot_path}")

# -------- Frame Loss Bar Chart --------
frames_received = [tcp_summary["FramesReceived"][0], udp_summary["FramesReceived"][0]]
frames_lost = [tcp_summary["FramesLost"][0], udp_summary["FramesLost"][0]]

x_labels = ["TCP", "UDP"]

plt.figure(figsize=(6, 4))
bar_width = 0.35
x = range(len(x_labels))

plt.bar(x, frames_received, width=bar_width, label="Received", color="green")
plt.bar([i + bar_width for i in x], frames_lost, width=bar_width, label="Lost", color="red")
plt.xticks([i + bar_width / 2 for i in x], x_labels)
plt.ylabel("Frame Count")
plt.title("Frame Loss Comparison: TCP vs UDP (Token Bucket)")
plt.legend()
plt.tight_layout()
loss_plot_path = os.path.join(PLOT_DIR, "frame_loss_comparison_token_bucket_tcp_vs_udp.png")
plt.savefig(loss_plot_path)
print(f"[+] Saved frame loss comparison plot: {loss_plot_path}")

