import sys
sys.path.append('/usr/lib/grass83/etc/python')

import os
from grass.script import setup as gsetup
from grass.script import run_command, read_command

gisdb = "grassdata"
location = "my_location"
mapset = "PERMANENT"
image_path = "combined_image_b_.bmp"
output_vector = "output_vector"
smoothed_vector = "smooth_vector"

north, east = 11.07124, 77.011059 
south, west = 11.070540, 77.004476

gsetup.init(gisdb, location, mapset)

run_command("r.in.gdal", input=image_path, output="binary_raster",overwrite=True)
run_command("g.list", type="raster")


run_command("g.region", raster="binary_raster")
run_command("g.region", raster="binary_raster", n=north, e=east, s=south, w=west)

run_command("r.null", map="binary_raster", setnull=0)
run_command("r.thin", input="binary_raster", output="thinned_raster",overwrite=True)

run_command("r.to.vect", input="thinned_raster", output=output_vector, type="line",overwrite=True)

run_command("v.generalize", input=output_vector, output=smoothed_vector, method="chaiken", threshold=0.5,overwrite=True)

run_command("v.db.droptable", map=smoothed_vector, flags="f") 
run_command(
    "v.category",
    input=smoothed_vector,
    output="simplified_vector",
    option="del",  # Delete all category fields
    overwrite=True,
)

run_command("v.out.ogr", input=smoothed_vector, output="output.shp", format="ESRI_Shapefile")
print(f"Vector data exported to 'output.shp'")