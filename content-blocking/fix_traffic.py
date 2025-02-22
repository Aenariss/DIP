# Temporary file to rename files in traffic folder, to assist with putting together separate fragments of traffic because selenium loves to wantonly crash 

from source.constants import TRAFFIC_FOLDER


import os

add_number = 922

for file in os.listdir(TRAFFIC_FOLDER):
    if file == ".empty":
        continue
    f = file.split('_')
    file_number = int(f[0])
    new_file_number = file_number + add_number
    new_file = str(new_file_number) + '_' + f[1]

    print(file, new_file)
    #os.rename(TRAFFIC_FOLDER + file, TRAFFIC_FOLDER + new_file)

