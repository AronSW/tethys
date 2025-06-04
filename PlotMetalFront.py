import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_bar_by_size_distance(file_path):
    # Load and clean data
    df = pd.read_excel(file_path)
    df = df.rename(columns={'filename': 'Distance', 'Column1': 'Size'})
    df = df.dropna(subset=['Distance', 'Size', 'RH1_avg', 'RL1_avg'])

    # Normalize and sort
    df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
    df = df.dropna(subset=['Distance'])
    df['Distance'] = df['Distance'].astype(int)
    df = df.sort_values(by='Distance')

    # Define constants
    sizes = ['S', 'M', 'B']
    distances = [50, 100, 150, 200, 250]
    colors = {'S': 'blue', 'M': 'green', 'B': 'red'}

    # Plotting function
    def plot_metric(metric, title, ylabel):
        bar_width = 0.25
        x = np.arange(len(distances))

        plt.figure(figsize=(10, 5))

        for i, size in enumerate(sizes):
            values = []
            for d in distances:
                val = df[(df['Size'] == size) & (df['Distance'] == d)][metric]
                values.append(val.values[0] if not val.empty else 0)
            plt.bar(x + i * bar_width, values, width=bar_width, label=f'Size {size}', color=colors[size])

        plt.xticks(x + bar_width, distances)
        plt.xlabel("Distance (cm)")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.grid(axis='y')
        plt.show()

    # Plot RH1 and RL1
    plot_metric('RH1_avg', 'RH1_avg by Distance and Size', 'RH1_avg')
    plot_metric('RL1_avg', 'RL1_avg by Distance and Size', 'RL1_avg')


plot_bar_by_size_distance(r"Documents\ETH\Tethys\Tests\Outputs\LandDay1\MetalUnder\Rawfiles\averaged_RH1_RL1_summary_with_metadata.xlsx")
