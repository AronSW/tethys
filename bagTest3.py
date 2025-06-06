import bagpy
from bagpy import bagreader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# === CONFIGURATION ===
bag_path = r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\bigMetalTransit\data_recording.bag"
output_csv = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\rh1_threshold_table.csv"
output_plot = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\rh1_threshold_plot.png"

threshold = 150         # Minimum RH1 signal to include
exclusion_windows = [
    (500, 600),
    (950, 1000),
    (1350, 1400)  # Add more as needed
]


# === ENSURE OUTPUT DIRECTORY EXISTS ===
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# === LOAD BAG ===
bag = bagreader(bag_path)
rh1_csv = bag.message_by_topic('/uuvx_UXB02/metal_detector_0/rh1')
alt_csv = bag.message_by_topic('/uuvx_UXB02/dvl_0/altitude')
depth_csv = bag.message_by_topic('/uuvx_UXB02/keller_sensor/depth_base')
twist_csv = bag.message_by_topic('/uuvx_UXB02/dvl_0/twist')

# === READ CSV FILES ===
rh1_df = pd.read_csv(rh1_csv)
alt_df = pd.read_csv(alt_csv)
depth_df = pd.read_csv(depth_csv)
twist_df = pd.read_csv(twist_csv)

# === NORMALIZE TIMES ===
rh1_df['Time'] -= rh1_df['Time'].min()
alt_df['Time'] -= alt_df['Time'].min()
depth_df['Time'] -= depth_df['Time'].min()
twist_df['Time'] -= twist_df['Time'].min()

# === COMPUTE SPEED FROM TWIST ===
twist_df['speed'] = np.sqrt(
    twist_df['twist.twist.linear.x']**2 +
    twist_df['twist.twist.linear.y']**2 +
    twist_df['twist.twist.linear.z']**2
)

# === SELECT RH1 VALUES ABOVE THRESHOLD ===
valid_rh1 = rh1_df[rh1_df['data'] >= threshold].copy()

for start, end in exclusion_windows:
    valid_rh1 = valid_rh1[~((valid_rh1['Time'] >= start) & (valid_rh1['Time'] <= end))]

# === INTERPOLATE ALTITUDE, DEPTH, SPEED ===
times = valid_rh1['Time'].values
signal = valid_rh1['data'].values
alt_interp = np.interp(times, alt_df['Time'], alt_df['point.z'])
depth_interp = np.interp(times, depth_df['Time'], depth_df['point.z'])
speed_interp = np.interp(times, twist_df['Time'], twist_df['speed'])

# === EXCLUDE PHYSICALLY IMPOSSIBLE MEASUREMENTS ===
valid_mask = (-depth_interp + alt_interp) <= 2.0
times = times[valid_mask]
signal = signal[valid_mask]
alt_interp = alt_interp[valid_mask]
depth_interp = depth_interp[valid_mask]
speed_interp = speed_interp[valid_mask]

# === CREATE FINAL DATAFRAME ===
df = pd.DataFrame({
    'Time': times,
    'RH1_strength': signal,
    'Altitude': alt_interp,
    'Depth': depth_interp,
    'Speed': speed_interp
})
df.to_csv(output_csv, index=False)

# === PLOT ===
plt.figure(figsize=(10, 6))
sc = plt.scatter(df['Altitude'], df['RH1_strength'], c=df['Speed'], cmap='viridis')
plt.xlabel("Altitude (m)")
plt.ylabel("RH1 Strength")
plt.colorbar(sc, label="ROV Speed (m/s)")
plt.title(f"RH1 Strength > {threshold} vs. Altitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_plot)
plt.show()
