import matplotlib.pyplot as plt
import numpy as np

# Data for scenarios
scenarios = ['Direct (No LB)', 'Bash Script LB', 'Python Ai LB']

total_requests = [23783, 11664, 16912]
requests_sec = [791, 388, 563]
avg_latency = [23.54, 9.23, 14.51]  # in ms
socket_errors = [6, 78, 23]  # read + timeout combined (6=0+6, 78=62+16, 23=9+14)
requests_unknown = [0, 62, 9]

server1_requests = [0, 6720, 8262]
server2_requests = [23790, 4888, 8651]

x = np.arange(len(scenarios))
width = 0.25

fig, axs = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle('Load Balancer Performance Comparison', fontsize=16)

# Total Requests
axs[0,0].bar(x, total_requests, color=['red', 'orange', 'green'])
axs[0,0].set_title('Total Requests')
axs[0,0].set_xticks(x)
axs[0,0].set_xticklabels(scenarios, rotation=15)

# Requests per second
axs[0,1].bar(x, requests_sec, color=['red', 'orange', 'green'])
axs[0,1].set_title('Requests per Second')
axs[0,1].set_xticks(x)
axs[0,1].set_xticklabels(scenarios, rotation=15)

# Average Latency (ms)
axs[1,0].bar(x, avg_latency, color=['red', 'orange', 'green'])
axs[1,0].set_title('Average Latency (ms)')
axs[1,0].set_xticks(x)
axs[1,0].set_xticklabels(scenarios, rotation=15)

# Socket Errors
axs[1,1].bar(x, socket_errors, color=['red', 'orange', 'green'])
axs[1,1].set_title('Socket Errors (read + timeout)')
axs[1,1].set_xticks(x)
axs[1,1].set_xticklabels(scenarios, rotation=15)

# Requests to Unknown Server
axs[2,0].bar(x, requests_unknown, color=['red', 'orange', 'green'])
axs[2,0].set_title('Misrouted Requests (to an invalid IP)')
axs[2,0].set_xticks(x)
axs[2,0].set_xticklabels(scenarios, rotation=15)

# Requests per backend server (side by side bars)
axs[2,1].bar(x - width/2, server1_requests, width, label='Server 1 (172.28.1.11)', color='blue')
axs[2,1].bar(x + width/2, server2_requests, width, label='Server 2 (172.28.1.12)', color='purple')
axs[2,1].set_title('Requests per Backend Server')
axs[2,1].set_xticks(x)
axs[2,1].set_xticklabels(scenarios, rotation=15)
axs[2,1].legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("lb_comparison.png")
print("Saved visualization as lb_comparison.png")

