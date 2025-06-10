import pandas as pd
import os
import glob

def analyze_segments(file_path):
    try:
        df = pd.read_csv(file_path)

        # Step 1: Identify annotations and clean data
        if 'RH1' in df.columns and df['RH1'].astype(str).str.contains("THRUSTER", na=False).any():
            annotations = df[df['RH1'].astype(str).str.contains("THRUSTER", na=False)].copy()
            df_clean = df[~df['RH1'].astype(str).str.contains("THRUSTER", na=False)].copy()
        elif 'RH1' in df.columns and df['RH1'].isna().any() and df['Timestamp'].astype(str).str.contains("THRUSTER", na=False).any():
            annotations = df[df['RH1'].isna() & df['Timestamp'].astype(str).str.contains("THRUSTER", na=False)].copy()
            df_clean = df[~(df['RH1'].isna() & df['Timestamp'].astype(str).str.contains("THRUSTER", na=False))].copy()
        else:
            annotations = pd.DataFrame()
            df_clean = df.copy()

        # Step 2: Clean and parse timestamps
        df_clean['Timestamp'] = pd.to_datetime(df_clean['Timestamp'], errors='coerce')
        df_clean = df_clean.dropna(subset=['Timestamp'])
        df_clean = df_clean.iloc[1:]

        df_clean['RH1'] = pd.to_numeric(df_clean['RH1'], errors='coerce')
        df_clean['RL1'] = pd.to_numeric(df_clean['RL1'], errors='coerce')
        df_clean = df_clean.dropna(subset=['RH1', 'RL1'])

        # Step 3: Parse annotation timestamps using next row
        annotation_records = []
        for i, row in annotations.iterrows():
            if i + 1 < len(df):
                ts = pd.to_datetime(df.iloc[i + 1]['Timestamp'], errors='coerce')
                if not pd.isna(ts):
                    label = str(row['Timestamp']).replace("THRUSTER CHANGE -> ", "")
                    annotation_records.append((ts, label))

        # Create segment boundaries
        if not annotation_records:
            # No segments → one full segment
            segment_results = [{
                'filename': os.path.basename(file_path),
                'thruster_label': "Full test",
                'RH1_avg': df_clean['RH1'].mean(),
                'RH1_max': df_clean['RH1'].max(),
                'RL1_avg': df_clean['RL1'].mean(),
                'RL1_max': df_clean['RL1'].max()
            }]
            return segment_results

        # Step 4: Segment by annotation timestamps
        segment_results = []
        starts = [df_clean['Timestamp'].iloc[0]] + [r[0] for r in annotation_records]
        labels = [r[1] for r in annotation_records] + ["End"]
        ends = starts[1:] + [df_clean['Timestamp'].iloc[-1]]

        for start, end, label in zip(starts, ends, labels):
            seg = df_clean[(df_clean['Timestamp'] >= start) & (df_clean['Timestamp'] < end)].copy()

            # Drop the first and last row from each segment
            if len(seg) > 2:
                seg = seg.iloc[1:-1]
            else:
                continue  # skip if not enough points left

            
            
            if len(seg) < 2:
                continue  # skip too-short segments
            segment_results.append({
                'filename': os.path.basename(file_path),
                'thruster_label': label,
                'RH1_avg': seg['RH1'].mean(),
                'RH1_max': seg['RH1'].max(),
                'RL1_avg': seg['RL1'].mean(),
                'RL1_max': seg['RL1'].max()
            })

        return segment_results

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return []

if __name__ == "__main__":
    folder_path = r"Documents\ETH\Tethys\Tests\Outputs\LandDay2\FluxTest\Rawfiles"
    file_pattern = os.path.join(folder_path, "*.csv")
    output_path = os.path.join(folder_path, "segmented_thruster_summary.csv")

    all_results = []

    for file_path in glob.glob(file_pattern):
        results = analyze_segments(file_path)
        all_results.extend(results)

    summary_df = pd.DataFrame(all_results)
    summary_df.to_csv(output_path, index=False)
    print(f"Saved segmented summary to: {output_path}")

