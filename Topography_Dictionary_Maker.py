import os

# This program has mostly been used by me just trying
# to wrangle the LIDAR data into something I can work with.
# You can probably just ignore this.

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

name = f"coordinate_topography_map.txt"
name2 = f"coordinate_topography_csv.txt"
file2 = open(name2, 'a')

topography_map = []
with open(os.path.join(location, name), "r") as file:
    line = file.readline()
    split_line = line.split("], [")
    for s_line in split_line:
        s_line = s_line.rstrip(']')
        s_line = s_line.lstrip('[')
        unwrapped = s_line.split(',')
        row = []
        for z in unwrapped:
            row.append(float(z))
        topography_map.append(row)

for y, row in enumerate(topography_map):
    for x, element in enumerate(row):
        point = f"{y},{x},{element}\n"
        file2.write(point)


file.close()
file2.close()
