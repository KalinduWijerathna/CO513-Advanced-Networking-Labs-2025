import pandas as pd
import matplotlib.pyplot as plt
import os

# Directories and files (adjust paths if needed)
LOG_DIR = "../logs"
PLOT_DIR = "./"
os.makedirs(PLOT_DIR, exist_ok=True)

resolutions = ["270p", "720p", "1080p"]
algorithms = ["leaky_bucket", "token_bucket"]

# 1. Latency comparison plots by resolution
for res in resolutions:
    plt.figure(figsize=(12, 6))
    
    for algo in algorithms:
        latency_file = os.path.join(LOG_DIR, f"latency_data_{algo}_{res}.csv")
        if not os.path.exists(latency_file):
            print(f"[!] Missing file: {latency_file}")
            continue
        
        df = pd.read_csv(latency_file)
        plt.plot(df["FrameID"], df["LatencySeconds"], label=algo.replace("_", " ").title())
    
    plt.title(f"Latency Comparison for {res.upper()} (Leaky Bucket vs Token Bucket)")
    plt.xlabel("Frame ID")
    plt.ylabel("Latency (seconds)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    plot_path = os.path.join(PLOT_DIR, f"latency_comparison_{res}.png")
    plt.savefig(plot_path)
    print(f"[+] Saved latency comparison plot: {plot_path}")
    plt.close()

# 2. Summary stats comparison plots by resolution
for res in resolutions:
    plt.figure(figsize=(10, 5))
    
    received = []
    lost = []
    labels = []
    
    for algo in algorithms:
        summary_file = os.path.join(LOG_DIR, f"summary_stats_{algo}_{res}.csv")
        if not os.path.exists(summary_file):
            print(f"[!] Missing file: {summary_file}")
            continue
        
        df = pd.read_csv(summary_file)
        frames_received = df["FramesReceived"].iloc[0]
        frames_lost = df["FramesLost"].iloc[0]
        
        received.append(frames_received)
        lost.append(frames_lost)
        labels.append(algo.replace("_", " ").title())
    
    x = range(len(labels))
    width = 0.35
    
    plt.bar(x, received, width, label="Frames Received", color="green")
    plt.bar([i + width for i in x], lost, width, label="Frames Lost", color="red")
    
    plt.xticks([i + width/2 for i in x], labels)
    plt.ylabel("Number of Frames")
    plt.title(f"Frame Reception Summary for {res.upper()} (Leaky Bucket vs Token Bucket)")
    plt.legend()
    plt.tight_layout()
    
    plot_path = os.path.join(PLOT_DIR, f"summary_comparison_{res}.png")
    plt.savefig(plot_path)
    print(f"[+] Saved summary comparison plot: {plot_path}")
    plt.close()

