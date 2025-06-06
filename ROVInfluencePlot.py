import bagpy
from bagpy import bagreader
import pandas as pd
import matplotlib.pyplot as plt
import os

# === INPUT: list of bag files ===
bag_files = [
    # WaterDay3 Thruster off
    r"C:\Users\aron\Documents\ETH\Tethys\Tests\WaterDay3\ROVInfluenceTest\inWaterThrusterOff\data_recording.bag",
    # WaterDay2 Thruster off
    r"C:\Users\aron\Documents\ETH\Tethys\Tests\250522_T_Küssnacht_Joerg_metaldetector\steadyThrustersOff\data_recording.bag",
    # WaterDay3 Hovering
    #r"C:\Users\aron\Documents\ETH\Tethys\Tests\WaterDay3\ROVInfluenceTest\steadyThrusterOn\data_recording.bag",
    # WaterDay1 Constant forward thrust
    #r"C:\Users\aron\Documents\ETH\Tethys\Tests\250520_T_Tiefenbrunnen_magnetometer\forwardThrusterConst1\data_recording.bag",
    # WaterDay1 Slow movement forward, set by computer
    #r"C:\Users\aron\Documents\ETH\Tethys\Tests\250520_T_Tiefenbrunnen_magnetometer\forwardConstantMovement2\data_recording.bag",
    # WaterDay4 Constant speed, DVL off
    #r"C:\Users\aron\Documents\ETH\Tethys\Tests\WaterDay3\ROVInfluenceTest\constSpeedDVLOff\data_recording.bag",
    # WaterDay4 Thruster off
    r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\steadyInWaterThrusterOff\data_recording.bag"
]

# === RESULT STORAGE ===
results = []

for bag_path in bag_files:
    print(f"Processing {bag_path}")
    bag = bagreader(bag_path)

    try:
        rh1_csv = bag.message_by_topic('/uuvx_UXB02/metal_detector_0/rh1')
        df = pd.read_csv(rh1_csv)
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df.dropna(subset=['Time'], inplace=True)

        mean_val = df['data'].mean()
        max_val = df['data'].max()
        label = os.path.basename(os.path.dirname(bag_path))

        results.append({
            'Label': label,
            'Average RH1': mean_val,
            'Max RH1': max_val
        })

    except Exception as e:
        print(f"Failed to process {bag_path}: {e}")

# === BUILD DATAFRAME ===
summary_df = pd.DataFrame(results)

# === PLOT 1: AVERAGE RH1 ===
plt.figure(figsize=(8, 5))
plt.bar(summary_df['Label'], summary_df['Average RH1'], color='blue')
plt.ylabel("Average Sensor Value")
plt.title("ROV influence")

plt.grid(axis='y')
plt.tight_layout()
plt.savefig("average_ROV_influence.png")
plt.show()

# === PLOT 2: MAX RH1 ===
plt.figure(figsize=(8, 5))
plt.bar(summary_df['Label'], summary_df['Max RH1'], color='red')
plt.ylabel("Max RH1 Value")
plt.title("Max RH1 per Rosbag")

plt.grid(axis='y')
plt.tight_layout()
plt.savefig("max_rh1_comparison.png")
plt.show()
