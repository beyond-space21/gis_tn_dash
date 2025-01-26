import os
from grass_session import Session
from grass.script import core as gcore

# Define paths for GIS database, location, and mapset
gisdb = "grassdata"  # Replace with your desired GIS database path
mapset = "PERMANENT"      # Mapset name (use "PERMANENT" or another name)

def create_env(location):
    # Check if GISDB directory exists, if not, create it
    if not os.path.exists(gisdb):
        os.makedirs(gisdb)

    # Initialize the GRASS session
    with Session(gisdb=gisdb, location=location, mapset=mapset) as session:
        # Check if the location exists; if not, create it
        location_path = os.path.join(gisdb, location)
        if not os.path.exists(location_path):
            print(f"Creating location: {location}")
            gcore.create_location(gisdb, location, epsg=4326)  # EPSG:4326 for WGS84 CRS

        # Switch to the "PERMANENT" mapset within the location
        print(f"Switching to mapset: {mapset}")
        if mapset != "PERMANENT":
            # Create the mapset if it does not exist
            mapset_path = os.path.join(location_path, mapset)
            if not os.path.exists(mapset_path):
                gcore.run_command("g.mapset", mapset=mapset, flags="c")
        print("GIS environment successfully initialized!")
