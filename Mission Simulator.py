import os
import shutil
import time

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
filepath = os.path.join(location, 'downlink.txt')


def coordinate_topography():
    src_file = os.path.join(location, "coordinate_topography_map_downlink.txt")
    dup = src_file + ".dup"
    shutil.copy(src_file, dup)

    dst_file = os.path.join(location, "coordinate_topography_map_downlink.txt.dup")
    new_dst_file_name = os.path.join(location, "downlink.txt")
    os.rename(dst_file, new_dst_file_name)


time.sleep(1)
dst = ["navigation\n", "coordinates\n", "mission control\n", "(749, 574, 1117.56)"]
f = open("downlink.txt", "w")
f.writelines(dst)
f.close()

time.sleep(4)
rvr = ["navigation\n", "coordinates\n", "mps orbiter\n", "(1328, 823, 1101.89)"]
f = open("downlink.txt", "w")
f.writelines(rvr)
f.close()

time.sleep(5)
coordinate_topography()
