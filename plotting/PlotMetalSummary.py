import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_bar_by_size_distance_fixed(file_path):
    # Load and clean data
    df = pd.read_csv(file_path)
    df = df.rename(columns={'Distance': 'Distance_cm'})  # normalize column name if needed
    df['Distance_cm'] = pd.to_numeric(df['Distance_cm'], errors='coerce')
    df = df.sort_values(by='Distance_cm')

    # Define plot settings
    sizes = ['S', 'M', 'B']
    distances = [50, 100, 150, 200]
    colors = {'S': 'blue', 'M': 'green', 'B': 'red'}
    metrics = [
        ('RH1_avg', 'RH1_avg by Distance and Size', 'RH1_avg'),
        ('RL1_avg', 'RL1_avg by Distance and Size', 'RL1_avg'),
        ('RH1_max', 'RH1_max by Distance and Size', 'RH1_max'),
        ('RL1_max', 'RL1_max by Distance and Size', 'RL1_max'),
    ]

    # Extract the baseline row
    baseline_row = df[df['filename'].str.contains("Base", case=False, na=False)].iloc[0]

    def plot_metric(metric, title, ylabel):
        bar_width = 0.25
        x = np.arange(len(distances) + 1)  # One slot for baseline

        plt.figure(figsize=(11, 5))

        for i, size in enumerate(sizes):
            values = [baseline_row[metric]]  # Baseline for each size
            for d in distances:
                val = df[(df['Size'] == size) & (df['Distance_cm'] == d)][metric]
                values.append(val.values[0] if not val.empty else 0)
            plt.bar(x + i * bar_width, values, width=bar_width, label=f'Size {size}', color=colors[size])

        plt.xticks(x + bar_width, ['Baseline'] + [str(d) for d in distances])
        plt.xlabel("Distance (cm)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.grid(axis='y')
        plt.show()

    # Plot all metrics
    for metric, title, ylabel in metrics:
        if metric in df.columns:
            plot_metric(metric, title, ylabel)
        else:
            print(f"Column {metric} not found in file.")

# Example usage
plot_bar_by_size_distance_fixed(r"Documents\ETH\Tethys\Tests\Outputs\LandDay1\MetalUnder\Rawfiles\RH1_RL1_summary_normalized.csv")
