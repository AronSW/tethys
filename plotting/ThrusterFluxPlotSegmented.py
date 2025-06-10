import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

def parse_filename_metadata(fname):
    distance_match = re.search(r'(\d+)(cm|dm|m)', fname)
    angle_match = re.search(r'(\d{1,3})d', fname)
    shield_match = re.search(r'(Filtered|Forniklet|Metal)', fname, re.IGNORECASE)

    distance_cm = None
    if distance_match:
        value, unit = distance_match.groups()
        value = int(value)
        if unit == 'cm':
            distance_cm = value
        elif unit == 'dm':
            distance_cm = value * 10
        elif unit == 'm':
            distance_cm = value * 100

    angle_deg = int(angle_match.group(1)) if angle_match else 0
    shield = shield_match.group(1).capitalize() if shield_match else 'None'

    return distance_cm, angle_deg, shield

def plot_thruster_analysis(file_path, output_dir="thruster_plots"):
    df = pd.read_csv(file_path)

    # Remove non-relevant labels
    df = df[~df['thruster_label'].str.contains("End", case=False, na=False)]
    df = df[~df['thruster_label'].str.contains("Full test", case=False, na=False)]

    # Extract metadata
    df[['Distance_cm', 'Angle_deg', 'Shielding']] = df['filename'].apply(
        lambda x: pd.Series(parse_filename_metadata(x))
    )

    os.makedirs(output_dir, exist_ok=True)

    # Convert thruster_label to string (if needed)
    
    df['thruster_label'] = df['thruster_label'].astype(str)

    # Extract numeric thrust value from the label
    def extract_thrust_value(label):
        match = re.search(r'(-?\d+)', label)
        return int(match.group(1)) if match else 0

    df['thrust_value'] = df['thruster_label'].apply(extract_thrust_value)


        # ---- Plot 4: Bar Plot by (Material, Distance_cm) for each thruster level ----
    for metric in ['RH1_avg', 'RL1_avg']:
        plt.figure(figsize=(18, 8))

        # Create combined label for each test config
        df['config_label'] = df.apply(lambda row: f"{row['Shielding']}_{int(row['Distance_cm'])}cm", axis=1)

        # Sort config labels by distance then material
        config_order = sorted(df[['config_label', 'Distance_cm', 'Shielding']].drop_duplicates().values.tolist(), key=lambda x: (x[1], x[2]))
        config_labels = [c[0] for c in config_order]
        x = np.arange(len(config_labels))

        bar_width = 0.08
        thrusts = sorted(df['thrust_value'].unique())

        for i, t in enumerate(thrusts):
            subset = df[df['thrust_value'] == t]
            vals = []
            for label in config_labels:
                val = subset[subset['config_label'] == label][metric].mean() if not subset[subset['config_label'] == label].empty else 0
                vals.append(val)
            plt.bar(x + i * bar_width, vals, width=bar_width, label=str(t))

        plt.xticks(x + bar_width * len(thrusts) / 2, config_labels, rotation=90)
        plt.xlabel("Material and Distance")
        plt.ylabel(metric)
        plt.title(f"{metric} vs Material and Distance (grouped by thrust level)")
        plt.legend(title="Thrust")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}_bar_by_material_distance.png"))
        plt.close()



# Usage
plot_thruster_analysis(r"Documents\ETH\Tethys\Tests\Outputs\LandDay2\FluxTest\Rawfiles\segmented_thruster_summary.csv")
