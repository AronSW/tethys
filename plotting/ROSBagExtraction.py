import bagpy
from bagpy import bagreader
import pandas as pd
import os

def analyseRosbag_single_file(file_name, output_csv_path, start_time=0.0, end_time=None):
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
        df['Time'] = df['Time'] - df['Time'].min()  # normalize time
        dfs[label] = df

    # Create filtered DataFrame
    filtered_df = pd.DataFrame()
    base_time = dfs['RH1']['Time']  # assume consistent Time base
    filtered_df['Time'] = base_time[(base_time >= start_time) & (end_time is None or base_time <= end_time)].reset_index(drop=True)

    for label, df in dfs.items():
        mask = (df['Time'] >= start_time)
        if end_time is not None:
            mask &= (df['Time'] <= end_time)
        filtered_df[label] = df.loc[mask, 'data'].reset_index(drop=True)

    filtered_df.to_csv(output_csv_path, index=False)
    print(f"Saved CSV to: {output_csv_path}")


if __name__ == "__main__":
    # === USER INPUTS ===
    input_bag = r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\bigMetalTransit\data_recording.bag"
    output_csv = r"C:\Users\aron\Documents\ETH\Tethys\Tests\Outputs\WaterDay4\bigMetalTransit.csv"
    start_time = 0  # seconds from start
    end_time = 150    # seconds from start

    analyseRosbag_single_file(input_bag, output_csv, start_time, end_time)
