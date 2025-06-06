<<<<<<< HEAD:ROSbadAnalysis.py
import bagpy
from bagpy import bagreader

import pandas as pd
import matplotlib.pyplot as plt
import glob
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
        csv_file = bag.message_by_topic(topic)
        df = pd.read_csv(csv_file)
        dfs[label] = df

    plt.figure(figsize=(12, 6))
    for label, df in dfs.items():
        if start_time is not None:
            df = df[df['Time'] >= start_time]
        if end_time is not None:
            df = df[df['Time'] <= end_time]
        plt.plot(df['Time'], df['data'], label=label)

    plt.xlabel("Time (s)")
    plt.ylabel("Sensor Value")
    plt.title(os.path.basename(os.path.dirname(file_name)))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    #folder_path = r"Documents\ETH\Tethys\Tests\250520_T_Tiefenbrunnen_magnetometer"
    #folder_path = r"Documents\ETH\Tethys\Tests\WaterDay3\MetalTestWater"
    #folder_path = r"Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector"
    folder_path = r"Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector"

    
    bag_files = glob.glob(os.path.join(folder_path, "**", "*.bag"), recursive=True)
    

    for path_name in bag_files:
        print(f"\n=== Processing: {path_name} ===")
        output_name = os.path.basename(path_name).replace('.bag', '.png')
        output_path = os.path.join("Documents/ETH/Tethys/Tests/Outputs/WaterDay4", output_name)
    
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            analyseRosbag(path_name, output_path, start_time=140, end_time=200)
        except Exception as e:
            print(f"Failed to process {path_name}: {e}")
            continue
    
=======
import bagpy
from bagpy import bagreader

import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def analyseRosbag(file_name, output_path):
    bag = bagreader(file_name)

    topics = {
        'RH1': '/uuvx_UXB02/metal_detector_0/rh1',
        'RH1R': '/uuvx_UXB02/metal_detector_0/rh1r',
        'RL1': '/uuvx_UXB02/metal_detector_0/rl1',
        'RL1R': '/uuvx_UXB02/metal_detector_0/rl1r'
    }

    dfs = {}

    for label, topic in topics.items():
        csv_file = bag.message_by_topic(topic)
        df = pd.read_csv(csv_file)
        dfs[label] = df

    plt.figure(figsize=(12, 6))
    for label, df in dfs.items():
        plt.plot(df['Time'], df['data'], label=label)

    plt.xlabel("Time (s)")
    plt.ylabel("Sensor Value")
    plt.title(os.path.basename(os.path.dirname(path_name)))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

if __name__ == "__main__":
    #folder_path = r"Documents\ETH\Tethys\Tests\250520_T_Tiefenbrunnen_magnetometer"
    folder_path = r"Documents\ETH\Tethys\Tests\WaterDay3\MetalTestWater"
    #folder_path = r"Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector"

    
    bag_files = glob.glob(os.path.join(folder_path, "**", "*.bag"), recursive=True)
    

    for path_name in bag_files:
        print(f"\n=== Processing: {path_name} ===")
        #output_path = f"Documents/ETH/Tethys/Tests/250520_T_Tiefenbrunnen_magnetometer/Output/{os.path.basename(os.path.dirname(path_name)).replace('.bag', '.png')}"
        output_path = f"Documents/ETH/Tethys/Tests/WaterDay3/Output/{os.path.basename(os.path.dirname(path_name)).replace('.bag', '.png')}"
        #output_path = f"Documents\ETH/Tethys/Tests/250603_T_Tiefenbrunnen_metal_detector/Output/{os.path.basename(os.path.dirname(path_name)).replace('.bag', '.png')}"
        try:
            analyseRosbag(path_name, output_path)
        except Exception as e: 
            print(f"Failed to process {path_name}: {e}")
            continue
    
>>>>>>> 7cc7d38d2ec464aefdcc91ec88480c611fcf91dd:plotting/ROSbadAnalysis.py
