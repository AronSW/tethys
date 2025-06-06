import bagpy
from bagpy import bagreader
import pandas as pd
import matplotlib.pyplot as plt
import os

def analyseRosbag(file_name, output_path, start_time=None, end_time=None):
    bag = bagreader(file_name)

    topics = {
        'RH1': '/uuvx_UXB02/metal_detector_0/rh1',
        'RH1R': '/uuvx_UXB02/metal_detector_0/rh1r',
        'RL1': '/uuvx_UXB02/metal_detector_0/rl1',
        'RL1R': '/uuvx_UXB02/metal_detector_0/rl1r'
    }

    dfs = {}
    for label, topic in topics.items():
        try:
            csv_file = bag.message_by_topic(topic)
            df = pd.read_csv(csv_file)
            dfs[label] = df
        except Exception as e:
            print(f"Could not read topic {topic}: {e}")

    # Compute minimum timestamp across all topics
    min_time = min(df['Time'].min() for df in dfs.values())
    for label in dfs:
      dfs[label]['Time'] -= min_time



    if not dfs:
        print("No valid data found.")
        return
    print(f"{label} range: {df['Time'].min():.2f} to {df['Time'].max():.2f}")

    plt.figure(figsize=(12, 6))
    for label, df in dfs.items():
        if start_time is not None:
            df = df[df['Time'] >= start_time]
        if end_time is not None:
            df = df[df['Time'] <= end_time]
        if not df.empty:
            plt.plot(df['Time'], df['data'], label=label)

    plt.xlabel("Time (s)")
    plt.ylabel("Sensor Value")
    plt.title(os.path.basename(file_name))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.show()


if __name__ == "__main__":
    input_bag = r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\pipeSearch1\data_recording.bag"
    output_png = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\pipeSearch1Cropped2.png"
    
    analyseRosbag(input_bag, output_png, start_time=750, end_time=800)
