# OOI_STx_h2zarr.py
#   convert OOI South Tx cable data to zarr

import xarray as xr
import pandas as pd
import numpy as np
import os
import h5py
from tqdm import tqdm

file_dir = '/das_data2/h5files/'
file_list = os.listdir(file_dir)

# remove .aria2 files (only for debugging during transfer)
valid_idx = []
for k, file in enumerate(file_list):
    if file[-2] != 'a':
        valid_idx.append(k)
        
file_list = [file_list[i] for i in valid_idx]
file_list.sort()

files = [file_dir+file for file in file_list]

first_loop=True

for file in tqdm(files):
    hf = h5py.File(file)
    
    ds = xr.Dataset({
        'RawData':((['distance', 'time'], hf['Acquisition']['Raw[0]']['RawData'][:])),
        'RawDataTime':('time', hf['Acquisition']['Raw[0]']['RawDataTime'][:]),
        'GpBits':('time', hf['Acquisition']['Raw[0]']['Custom']['GpBits']),
        'GpsStatus':('time', hf['Acquisition']['Raw[0]']['Custom']['GpsStatus']),
        'PpsOffset':('time', hf['Acquisition']['Raw[0]']['Custom']['PpsOffset']),
        'SampleCount':('time', hf['Acquisition']['Raw[0]']['Custom']['SampleCount'])}
    )
    
    ds = ds.chunk({'time':3000, 'distance':3000})
    
    # create new zarr store if beginning of loop otherwize, append in time dimension
    if first_loop:
        first_loop = False
        ds.to_zarr(f'/das_data2/SouthCable_Tx_{files[0][-21:-4]}{files[-1][-21:-4]}', mode='w-')
    else:
        ds.to_zarr(f'/das_data2/SouthCable_Tx_{files[0][-21:-4]}{files[-1][-21:-4]}', append_dim='time')