import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load Excel file and target sheet
df = pd.read_excel(r"Documents\ETH\Tethys\Tests\Outputs\LandDay2\MetalMovementFront\CSVtoPlotMod.xlsx", sheet_name="averaged_RH1_RL1_summary")

# Ensure numeric types
df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
df = df.dropna(subset=['Distance'])
df['Distance'] = df['Distance'].astype(int)

# Define plot settings
df['Size'] = df['Size'].astype(str)
sizes = sorted(df['Size'].unique())
df = df[df['Distance'] != 50]


distances = sorted(df['Distance'].unique())
metrics = ['RH1_max', 'RL1_max']
colors = {'B': 'red', 'M': 'green', 'S': 'blue', 0: 'gray'}  # include baseline if present

# Bar plot function
import os

# Create output directory if not exists
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)



def plot_metric(metric):
    plt.figure(figsize=(12, 6))
    bar_width = 0.2
    x = np.arange(len(distances))

    for i, size in enumerate(sizes):
        subset = df[df['Size'] == size]
        values = []
        for d in distances:
            match = subset[subset['Distance'] == d]
            val = match[metric].mean() if not match.empty else 0
            values.append(val)
        plt.bar(x + i * bar_width, values, width=bar_width, label=f'Size {size}', color=colors.get(size, 'black'))

    plt.xticks(x + bar_width * len(sizes) / 2, [f"{d} cm" for d in distances])
    plt.xlabel("Distance")
    plt.ylabel(metric)
    plt.title(f"{metric} by Distance and Size")
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y')

    # Save and close
    save_path = os.path.join(output_dir, f"{metric}_bar_plot.png")
    plt.savefig(save_path)
    plt.close()
# Plot both metrics
for m in metrics:
    plot_metric(m)
