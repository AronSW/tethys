import pandas as pd
import os
import glob

def compute_averages(file_path):
    try:
        df = pd.read_csv(file_path)

        # Step 1: Detect and remove annotation rows
        if 'RH1' in df.columns and df['RH1'].astype(str).str.contains("THRUSTER", na=False).any():
            df_clean = df[~df['RH1'].astype(str).str.contains("THRUSTER", na=False)].copy()
        elif 'RH1' in df.columns and df['RH1'].isna().any() and df['Timestamp'].str.contains("THRUSTER", na=False).any():
            df_clean = df[~(df['RH1'].isna() & df['Timestamp'].str.contains("THRUSTER", na=False))].copy()
        else:
            df_clean = df.copy()

        # Step 2: Parse timestamps and remove first row
        df_clean.iloc[:, 0] = pd.to_datetime(df_clean.iloc[:, 0], errors='coerce')
        df_clean = df_clean.dropna(subset=[df_clean.columns[0]])
        df_clean = df_clean.iloc[1:]  # Drop first reading

        # Step 3: Ensure RH1 and RL1 are numeric
        df_clean['RH1'] = pd.to_numeric(df_clean['RH1'], errors='coerce')
        df_clean['RL1'] = pd.to_numeric(df_clean['RL1'], errors='coerce')
        df_clean = df_clean.dropna(subset=['RH1', 'RL1'])

        # Compute means
        rh1_avg = df['RH1'].mean()
        rl1_avg = df['RL1'].mean()

        # Compute max
        rh1_max = df['RH1'].max()
        rl1_max = df['RL1'].max()

        return {
            'filename': os.path.basename(file_path),
            'RH1_avg': rh1_avg,
            'RL1_avg': rl1_avg,
            'RH1_max': rh1_max,
            'RL1_max': rl1_max
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

    # Save to a new CSV
    summary_df = pd.DataFrame(summary_data)
    output_csv = os.path.join(folder_path, "averaged_RH1_RL1_summary.csv")
    summary_df.to_csv(output_csv, index=False)
    print(f"Saved summary to: {output_csv}")