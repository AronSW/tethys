import bagpy
from bagpy import bagreader
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import os

# === FILE PATHS ===
bag_path = r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\bigMetalTransit\data_recording.bag"
output_csv = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\spike_table.csv"
output_plot = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\spike_plot.png"

# === EXCLUSION WINDOWS (absolute time, will be shifted)
exclusion_windows = [
    (500, 700),
    (1250, 1450)
]


# === CREATE FOLDER IF NEEDED ===
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


# === NORMALIZE TIME TO BAG START ===
rh1_df['Time'] -= rh1_df['Time'].min()
alt_df['Time'] -= alt_df['Time'].min()
depth_df['Time'] -= depth_df['Time'].min()
twist_df['Time'] -= twist_df['Time'].min()

# === DETECT SPIKES IN RH1 ===
peaks, _ = find_peaks(rh1_df['data'], prominence=150)
spike_times = rh1_df['Time'].iloc[peaks]
spike_strengths = rh1_df['data'].iloc[peaks]

# === SHIFT EXCLUSION WINDOWS BASED ON RH1 TIME BASE ===
time_offset = rh1_df['Time'].min()
exclusion_windows = [(start - time_offset, end - time_offset) for start, end in exclusion_windows]

# === REMOVE SPIKES IN EXCLUSION ZONES ===
for start, end in exclusion_windows:
    mask = ~((spike_times >= start) & (spike_times <= end))
    spike_times = spike_times[mask]
    spike_strengths = spike_strengths[mask]

# === INTERPOLATE ALTITUDE & DEPTH ===
alt_interp = np.interp(spike_times, alt_df['Time'], alt_df['point.z'])
depth_interp = np.interp(spike_times, depth_df['Time'], depth_df['point.z'])

# === FILTER OUT SPIKES WHERE DEPTH + ALTITUDE > 2m ===
valid_mask = (-depth_interp + alt_interp) <= 2.0
spike_times = spike_times[valid_mask]
spike_strengths = spike_strengths[valid_mask]
alt_interp = alt_interp[valid_mask]
depth_interp = depth_interp[valid_mask]

# === INTERPOLATE SPEED FROM DVL TWIST ===
twist_df['speed'] = np.sqrt(
    twist_df['twist.twist.linear.x']**2 +
    twist_df['twist.twist.linear.y']**2 +
    twist_df['twist.twist.linear.z']**2
)
speed_interp = np.interp(spike_times, twist_df['Time'], twist_df['speed'])

# === CREATE SPIKE TABLE ===
spike_df = pd.DataFrame({
    'Time': spike_times,
    'RH1_strength': spike_strengths,
    'Altitude': alt_interp,
    'Depth': depth_interp,
    'Speed': speed_interp
})
spike_df.to_csv(output_csv, index=False)

# === PLOT ===
plt.figure(figsize=(10, 6))
sc = plt.scatter(spike_df['Altitude'], spike_df['RH1_strength'], c=spike_df['Speed'], cmap='viridis')
plt.xlabel("Altitude (m)")
plt.ylabel("RH1 Spike Strength")
plt.colorbar(sc, label="ROV Speed (m/s)")
plt.title("RH1 Spike Strength vs. Altitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_plot)
plt.show()
