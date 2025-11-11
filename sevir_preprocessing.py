import os
import h5py
import numpy as np
from tqdm import tqdm
import argparse


parser = argparse.ArgumentParser(description="Convert H5 dataset to individual compressed NPZ files")
parser.add_argument("--h5_path", type=str, required=True, help="Path to the input H5 file")
parser.add_argument("--save_dir", type=str, required=True, help="Directory to save output NPZ files")
args = parser.parse_args()

h5_path = args.h5_path
save_dir = args.save_dir

os.makedirs(save_dir, exist_ok=True)

with h5py.File(h5_path, 'r') as hf:
    IN = hf['IN']
    OUT = hf['OUT']
    
    for idx in tqdm(range(IN.shape[0])):
        in_sample = IN[idx]
        out_sample = OUT[idx]
        np.savez_compressed(
            os.path.join(save_dir, f'sample_{idx:05d}.npz'),
            IN=in_sample,
            OUT=out_sample
        )

print(f"Saved {IN.shape[0]} samples to {save_dir}")