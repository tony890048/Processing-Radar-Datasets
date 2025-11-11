import numpy as np
import datetime
import os
from tqdm import tqdm
import imageio
import argparse

parser = argparse.ArgumentParser(description="Download and extract MeteoNet dataset")
parser.add_argument("--path", type=str, required=True, help="Path to the dataset folder")
parser.add_argument("--region", type=str, default="SE", choices=["SE", "NW"], help="Region code, SE or NW")
parser.add_argument("--save_dir", type=str, default=".", help="Directory to save downloaded files")
args = parser.parse_args()


def process(img, region):
    if region == "NW":
        img = img[-416:, -416:]  # for NW
    else:
        img = img[:416, :416]   # for SE
    img[img == 255] = 0    # set uncovered radar region to 0
    img = img / 70.0
    return img.astype(np.float32) 


pbar = tqdm(desc="Processing all data")

for year in [2016, 2017, 2018]:
    for month in range(1, 13):
        for part_month in [1, 2, 3]:
            print(f"Processing Year: {year}, Month: {month}, Part: {part_month}")
            fname = os.path.join(
                        args.path,
                        f"{args.region}_reflectivity_{year}",
                        f"{args.region}_reflectivity_old_product_{year}",
                        f"reflectivity-old-{args.region}-{year}-{month:02d}",
                        f"reflectivity_old_{args.region}_{year}_{month:02d}.{part_month}.npz"
                    )            
            if os.path.exists(fname):
                d = np.load(fname, allow_pickle=True)
                data = d['data']
                dates = d['dates']

                num_data = data.shape[0]
                for i in tqdm(range(num_data)):
                    dt = dates[i]

                    year_str  = dt.strftime('%Y')  
                    month_str = dt.strftime('%m')
                    day_str   = dt.strftime('%d') 
                    hour_str  = dt.strftime('%H') 
                    minute_str= dt.strftime('%M') 

                    save_dir = os.path.join(
                        args.save_dir,
                        f"{args.region}",
                        year_str,
                        month_str,
                        day_str
                    )
                    os.makedirs(save_dir, exist_ok=True)

                    imageio.imwrite(f"{save_dir}/{dt.strftime('%Y%m%d%H%M')}.tiff", process(data[i], args.region))

                    pbar.update(1)  # 更新進度條

pbar.close()