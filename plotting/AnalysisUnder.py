import pandas as pd
import os
import glob
import re

def parse_metadata(filename):
    base = os.path.basename(filename)
    match = re.search(r'(Big|Medium|Small|B|M|S)(Side|Under|Front)?(\d+)(cm|dm|m)', base)
    if not match:
        return None, None, None

    # Normalize size
    raw_size = match.group(1)
    size_map = {'Big': 'B', 'Medium': 'M', 'Small': 'S'}
    size = size_map.get(raw_size, raw_size)  # Already B/M/S stay unchanged

    # Location (optional)
    location = match.group(2) or ""

    # Distance normalization to cm
    dist_value = int(match.group(3))
    unit = match.group(4)
    if unit == 'cm':
        distance_cm = dist_value
    elif unit == 'dm':
        distance_cm = dist_value * 10
    elif unit == 'm':
        distance_cm = dist_value * 100
    else:
        distance_cm = None

    return size, location, distance_cm

def compute_averages(file_path):
    try:
        df = pd.read_csv(file_path)

        # Remove annotations
        if 'RH1' in df.columns:
            df = df[~df['RH1'].astype(str).str.contains("THRUSTER", na=False)]

        # Convert columns
        df['RH1'] = pd.to_numeric(df['RH1'], errors='coerce')
        df['RL1'] = pd.to_numeric(df['RL1'], errors='coerce')
        df = df.dropna(subset=['RH1', 'RL1'])

        df = df.iloc[1:]  # Drop the first row


        # Compute means
        rh1_avg = df['RH1'].mean()
        rl1_avg = df['RL1'].mean()

        rh1_max = df['RH1'].max()
        rl1_max = df['RL1'].max()


        # Extract normalized metadata
        size, location, distance_cm = parse_metadata(file_path)

        return {
            'filename': os.path.basename(file_path),
            'RH1_avg': rh1_avg,
            'RL1_avg': rl1_avg,
            'RH1_max': rh1_max,
            'RL1_max': rl1_max,
            'Size': size,
            'Location': location,
            'Distance_cm': distance_cm
        }

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return None

if __name__ == "__main__":
    folder_path = r"Documents\ETH\Tethys\Tests\Outputs\LandDay1\MetalUnder\Rawfiles"
    file_pattern = os.path.join(folder_path, "*.csv")

    summary_data = []

    for file_path in glob.glob(file_pattern):
        result = compute_averages(file_path)
        if result:
            summary_data.append(result)

    summary_df = pd.DataFrame(summary_data)
    output_csv = os.path.join(folder_path, "RH1_RL1_summary_normalized.csv")
    summary_df.to_csv(output_csv, index=False)
    print(f"Saved normalized summary to: {output_csv}")
