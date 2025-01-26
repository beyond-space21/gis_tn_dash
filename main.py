import sys
sys.path.append('/usr/lib/grass83/etc/python')

import os
from grass.script import setup as gsetup
from grass.script import run_command, read_command

import grass_space as init
import tile_renderer
import uuid

gisdb = "grassdb"    
mapset = "PERMANENT"

grassdb_dir = "grassdb"
shp_dir = "shp"
raster_dir = "raster"
logs_dir = "logs"

if not os.path.exists(grassdb_dir):
       os.makedirs(grassdb_dir)
if not os.path.exists(shp_dir):
       os.makedirs(shp_dir)
if not os.path.exists(raster_dir):
       os.makedirs(raster_dir)
if not os.path.exists(logs_dir):
       os.makedirs(logs_dir)

def run_process(north,east,south,west,location,source_raster,output_raster,output_vector):
    smoothed_vector = output_raster+"_smth"

    gsetup.init(gisdb, location, mapset)

    sv_dir = "raster/"+source_raster

    if not os.path.exists(sv_dir):
       os.makedirs(sv_dir)

    run_command("r.in.gdal", input=sv_dir+'/'+source_raster+".bmp", output="binary_raster",overwrite=True)
    # run_command("g.list", type="raster")

    run_command("g.region", raster="binary_raster")
    run_command("g.region", raster="binary_raster", n=north, e=east, s=south, w=west)

    run_command("r.null", map="binary_raster", setnull=0)
    run_command("r.thin", input="binary_raster", output="thinned_raster",overwrite=True)

    run_command("r.to.vect", input="thinned_raster", output=output_raster, type="line",overwrite=True)

    run_command("v.generalize", input=output_raster, output=smoothed_vector, method="chaiken", threshold=0.5,overwrite=True)

    sp_dir = "shp/"+output_vector
    if not os.path.exists(sp_dir):
       os.makedirs(sp_dir)
    run_command("v.out.ogr", input=smoothed_vector, output=sp_dir+'/'+output_vector+".shp", format="ESRI_Shapefile")



north, east = 11.07124, 77.011059 
south, west = 11.070540, 77.004476

task_id = str(uuid.uuid1()).replace("-", "")
print("ID: ",task_id)

tile_renderer.render(north,east,south,west,task_id)
input("completed render")
init.create_env(task_id)
run_process(north,east,south,west,task_id,task_id,"raster_"+task_id,task_id)