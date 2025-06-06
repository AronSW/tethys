from bagpy import bagreader
import pandas as pd

bag_path = r"C:\Users\aron\Documents\ETH\Tethys\Tests\250603_T_Tiefenbrunnen_metal_detector\bigMetalTransit\data_recording.bag"

bag = bagreader(bag_path)


depth_csv = bag.message_by_topic('/uuvx_UXB02/dvl_0/twist')
depth_df = pd.read_csv(depth_csv)
print(depth_df.columns)