import os
from grass_session import Session
from grass.script import core as gcore

# Define paths for GIS database, location, and mapset
gisdb = "grassdb"  # Replace with your desired GIS database path
mapset = "PERMANENT"      # Mapset name (use "PERMANENT" or another name)

def create_env(location):
    with Session(gisdb=gisdb, location=location, mapset=mapset) as session:
        location_path = os.path.join(gisdb, location)
        if not os.path.exists(location_path):
            print(f"Creating location: {location}")
            gcore.create_location(gisdb, location, epsg=4326)

        print(f"Switching to mapset: {mapset}")
        if mapset != "PERMANENT":
            mapset_path = os.path.join(location_path, mapset)
            if not os.path.exists(mapset_path):
                gcore.run_command("g.mapset", mapset=mapset, flags="c")
        print("GIS environment successfully initialized!")
