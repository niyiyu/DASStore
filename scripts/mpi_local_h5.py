from mpi4py import MPI

import h5py
import numpy as np
from scipy import signal

# parallelize with ompi
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

channel_index = np.linspace(1000, 47000, 501)[:-1].astype(int)   # calculate peak amplitude for 500 channels
sos = signal.butter(2, [0.01, 1], 'bp', fs=200, output='sos')  # bandpass filter 0.01 Hz to 1 Hz
taper = np.hanning(120000)                 # taper to use


for idx, icha in enumerate(channel_index):
    if rank == 0:
        print(idx, flush = True)
    if idx % size == rank:
        d = np.zeros(120000)
        for i in range(10):
            # concatenate 10 minutes of data
            f = h5py.File(f"../data/South-C1-LR-95km-P1kHz-GL50m-SP2m-FS200Hz_2021-11-02T000{i}14Z.h5", mode = "r")
            d[i*12000:(i+1)*12000] = f['/Acquisition/Raw[0]/RawData'][icha, :]
            f.close()

        # some computing. demean, taper, filtering
        #d is the time series of shape 120,000 (10minutes@200Hz)
        d = d-np.mean(d)
        d *= taper
        filtered = signal.sosfilt(sos, d)
        m = filtered.max()
        # print(f"rank {rank}\t| {idx}\t| max: %.3f" % filtered.max(), flush = True)