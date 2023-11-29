import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read data from CSV file
df = pd.read_csv("metrics_text.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df[df["platform"] == "lightsail"]

# Plotting
plt.figure(figsize=(12, 6))

# Plotting CPU Utilization
plt.subplot(2, 2, 1)
sns.lineplot(x="timestamp", y="cpu_utilized", data=df, marker='o', label='CPU Utilization')
plt.title('CPU Utilization over Time')

# Plotting Memory Utilization
plt.subplot(2, 2, 2)
sns.lineplot(x="timestamp", y="vmemory_utilized", data=df, marker='o', label='Memory Utilization', color='orange')
plt.title('Memory Utilization over Time')

# Plotting Text Length
plt.subplot(2, 2, 3)
sns.barplot(x="id", y="text_length", data=df, palette='viridis')
plt.title('Text Length Comparison')

# Plotting Time Elapsed
plt.subplot(2, 2, 4)
sns.barplot(x="id", y="time_elapsed", data=df, palette='magma')
plt.title('Time Elapsed Comparison')

plt.tight_layout()
plt.show()
