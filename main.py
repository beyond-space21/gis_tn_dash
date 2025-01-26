import sys
sys.path.append('/usr/lib/grass83/etc/python')

import os
from grass.script import setup as gsetup
from grass.script import run_command, read_command

gisdb = "grassdata"
location = "my_location"

def run_process(north,east,south,west,mapset,source_raster,output_raster,output_vector):
    # mapset = "PERMANENT"
    # image_path = "combined_image_b_.bmp"
    # output_vector = "output_vector"
    smoothed_vector = output_raster+"_smth"

    gsetup.init(gisdb, location, mapset)

    run_command("r.in.gdal", input=source_raster, output="binary_raster",overwrite=True)
    run_command("g.list", type="raster")


    run_command("g.region", raster="binary_raster")
    run_command("g.region", raster="binary_raster", n=north, e=east, s=south, w=west)

    run_command("r.null", map="binary_raster", setnull=0)
    run_command("r.thin", input="binary_raster", output="thinned_raster",overwrite=True)

    run_command("r.to.vect", input="thinned_raster", output=output_raster, type="line",overwrite=True)

    run_command("v.generalize", input=output_raster, output=smoothed_vector, method="chaiken", threshold=0.5,overwrite=True)

    run_command("v.out.ogr", input=smoothed_vector, output=output_vector+".shp", format="ESRI_Shapefile")



north, east = 11.07124, 77.011059 
south, west = 11.070540, 77.004476
run_process(north,east,south,west,"PERMANENT","combined_image_b_.bmp","out_test","test_out_vec")