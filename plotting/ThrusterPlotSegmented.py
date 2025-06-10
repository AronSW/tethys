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


    # ---- Plot 1: Bar Plot - Effect of Distance (No Shielding) ----
    df_distance = df[df['Shielding'] == 'None']
    for metric in ['RH1_avg', 'RL1_avg']:
        plt.figure(figsize=(14, 6))

        sorted_labels_df = df[['thruster_label', 'thrust_value']].drop_duplicates().sort_values('thrust_value')
        labels = sorted_labels_df['thruster_label'].tolist()

        x = np.arange(len(labels))
        bar_width = 0.15
        distances = sorted(df_distance['Distance_cm'].dropna().unique())
        
        for i, d in enumerate(distances):
            subset = df_distance[df_distance['Distance_cm'] == d]
            vals = [subset[subset['thruster_label'] == label][metric].values[0] if not subset[subset['thruster_label'] == label].empty else 0 for label in labels]
            plt.bar(x + i * bar_width, vals, width=bar_width, label=f"{d} cm")

        plt.xticks(x + bar_width * len(distances) / 2, labels, rotation=45)
        plt.xlabel("Thruster Label")
        plt.ylabel(metric)
        plt.title(f"{metric} vs Thrust (Varying Distance, No Shielding)")
        plt.legend(title="Distance")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}_bar_by_distance.png"))
        plt.close()

    # ---- Plot 2: Bar Plot - Effect of Shielding (50 cm Only) ----
    df_shield = df[df['Distance_cm'] == 50]
    for metric in ['RH1_avg', 'RL1_avg']:
        plt.figure(figsize=(14, 6))
        
        sorted_labels_df = df[['thruster_label', 'thrust_value']].drop_duplicates().sort_values('thrust_value')
        labels = sorted_labels_df['thruster_label'].tolist()

        x = np.arange(len(labels))
        bar_width = 0.15
        shields = ['None', 'Forniklet', 'Filtered', 'Metal']
        
        for i, s in enumerate(shields):
            subset = df_shield[df_shield['Shielding'] == s]
            vals = [subset[subset['thruster_label'] == label][metric].values[0] if not subset[subset['thruster_label'] == label].empty else 0 for label in labels]
            plt.bar(x + i * bar_width, vals, width=bar_width, label=s)

        plt.xticks(x + bar_width * len(shields) / 2, labels, rotation=45)
        plt.xlabel("Thruster Label")
        plt.ylabel(metric)
        plt.title(f"{metric} vs Thrust (Shielding Comparison at 50 cm)")
        plt.legend(title="Shielding")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}_bar_by_shielding.png"))
        plt.close()

            # ---- Plot 3: Bar Plot - Effect of Angle (No Shielding) ----
    df_angle = df[df['Shielding'] == 'None']
    for metric in ['RH1_avg', 'RL1_avg']:
        plt.figure(figsize=(14, 6))
        
        sorted_labels_df = df[['thruster_label', 'thrust_value']].drop_duplicates().sort_values('thrust_value')
        labels = sorted_labels_df['thruster_label'].tolist()

        x = np.arange(len(labels))
        bar_width = 0.15
        angles = sorted(df_angle['Angle_deg'].dropna().unique())

        for i, angle in enumerate(angles):
            subset = df_angle[df_angle['Angle_deg'] == angle]
            vals = [subset[subset['thruster_label'] == label][metric].values[0] if not subset[subset['thruster_label'] == label].empty else 0 for label in labels]
            plt.bar(x + i * bar_width, vals, width=bar_width, label=f"{angle}°")

        plt.xticks(x + bar_width * len(angles) / 2, labels, rotation=45)
        plt.xlabel("Thruster Label")
        plt.ylabel(metric)
        plt.title(f"{metric} vs Thrust (Varying Angle, No Shielding)")
        plt.legend(title="Angle")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{metric}_bar_by_angle.png"))
        plt.close()


# Usage
plot_thruster_analysis(r"Documents\ETH\Tethys\Tests\Outputs\LandDay2\ThrusterTest\Rawfiles\segmented_thruster_summary.csv")
