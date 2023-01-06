# This downloads 32 files at a time. (There is probably a much more efficient way to do this)
sudo aria2c -j 32 -s 32 -x 16 -i download_list_left.txt -d /das_data2/h5files