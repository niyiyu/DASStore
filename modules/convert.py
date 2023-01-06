"""convert.py

collection of functions to convert DAS data in various formats to zarr store

Notes
-----
TODO we should decide if the zarr store inherits the data organization from the
original file (where zarr stores from different interigators might have different structure),
or define a uniform **DAS** format to the zarr stores that we create.

"""

import os
import h5py
import xarray as xr
from tqdm import tqdm

def h52zarr_xarray(h5_dir, fn_zarr, chunk={'time':3000, 'distance':3000}):
    '''
    converts multiple h5 files to single zarr store using xarray. Manually loads the data into memory
        for single h5 and then writes/appends to zarr using xarray
    
    TODO This is pretty slow right now. Theres probably a better way to read h5 into memory.

    Parameters
    ----------
    h5_dir : string
        absolute (local) path to all h5 files to be converted. Should be folder containing
        multiple h5 files. Currently, it is assumed that each file is sorted in order
        and the append dimension is time.
    fn_zarr : string
        location of zarr store
    chunk : dict
        how to chunk zarr store (default {'time':3000, 'distance':3000})
    '''

    file_list = os.listdir(h5_dir)
    file_list.sort()

    files = [h5_dir+file for file in file_list]

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
            ds.to_zarr(fn_zarr, mode='w-')
        else:
            ds.to_zarr(fn_zarr, append_dim='time')

    return