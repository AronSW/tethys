import pandas as pd
import matplotlib.pyplot as plt
import os
import glob




def plot_test_data(file_path, output_dir= "plots", delimiter = ","):
  try:
    df = pd.read_csv(file_path, delimiter = delimiter)

    if 'RH1' in df.columns and df['RH1'].astype(str).str.contains("THRUSTER", na=False).any():
        annotations = df[df['RH1'].astype(str).str.contains("THRUSTER", na=False)].copy()
        df_clean = df[~df['RH1'].astype(str).str.contains("THRUSTER", na=False)].copy()
    elif 'RH1' in df.columns and df['RH1'].isna().any() and df['Timestamp'].str.contains("THRUSTER", na=False).any():
        annotations = df[df['RH1'].isna() & df['Timestamp'].str.contains("THRUSTER", na=False)].copy()
        df_clean = df[~(df['RH1'].isna() & df['Timestamp'].str.contains("THRUSTER", na=False))].copy()
    else:
        annotations = pd.DataFrame()
        df_clean = df.copy()
    
    
    df_clean.iloc[:, 0] = pd.to_datetime(df_clean.iloc[:, 0], errors='coerce')
    df_clean = df_clean.dropna(subset=[df_clean.columns[0]])
    df_clean = df_clean.iloc[1:]

    
    plt.figure(figsize=(12, 5))
    for col in df_clean.columns[1:5]: 
        plt.plot(df_clean.iloc[:, 0], df_clean[col], label=col)

    for i, row in annotations.iterrows():
        if i + 1 < len(df):
            next_row = df.iloc[i + 1]
            try:
                timestamp = pd.to_datetime(next_row['Timestamp'])
                label = row['Timestamp'].replace("THRUSTER CHANGE -> ", "")
                plt.axvline(x=timestamp, color='red', linestyle='--', alpha=0.5)
                plt.text(timestamp, plt.ylim()[1]*0.95, label, rotation=90,
                         va='top', ha='right', fontsize=8, color='red')
            except:
                continue

    plt.xlabel("Timestamp")
    plt.ylabel("Sensor Value")
    plt.title(os.path.basename(file_path))
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.png")
    plt.savefig(output_path)

    plt.close()
  except Exception as e:
    print("ERROR", e)
    return None
  
if __name__ == "__main__":
  folder_path = r"Documents\ETH\Tethys\Tests\TestDay1"
  output_dir = os.path.join(folder_path, "plots")
  

  file_pattern = os.path.join(folder_path, "*.csv")
  for file_path in glob.glob(file_pattern):
    plot_test_data(file_path, output_dir=output_dir)
  
