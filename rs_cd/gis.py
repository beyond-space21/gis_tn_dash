import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.features import shapes
from shapely.geometry import shape
import geopandas as gpd
from PIL import Image

# Inputs
image = Image.open("combined_image_a.png").convert('1')  # Convert to 1-bit (binary) image
image = np.array(image,dtype=np.uint8)
 
height, width = image.shape
min_lon, min_lat = 11.070540,77.004476  # Bottom-left corner
max_lon, max_lat = 11.07124,77.011059  # Top-right corner
output_vector_path = "output_vector.geojson"


# Calculate pixel size
pixel_width = (max_lon - min_lon) / width
pixel_height = (min_lat - max_lat) / height  # Negative as latitude decreases

# Define transform
transform = from_origin(min_lon, max_lat, pixel_width, -pixel_height)

# Save raster to GeoTIFF
raster_path = "temp_raster.tif"
with rasterio.open(
    raster_path,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype=image.dtype,
    crs="EPSG:4326",  # WGS84 Latitude/Longitude
    transform=transform,
) as dst:
    dst.write(image, 1)

# Convert raster to vector
with rasterio.open(raster_path) as src:
    raster_data = src.read(1)
    transform = src.transform
    mask = raster_data > 0  # Binary mask
    shapes_generator = shapes(raster_data, mask=mask, transform=transform)

# Create GeoDataFrame
geometries = []
values = []
for geom, value in shapes_generator:
    geometries.append(shape(geom))
    values.append(value)

gdf = gpd.GeoDataFrame({'geometry': geometries, 'value': values}, crs="EPSG:4326")

# Save to GeoJSON
gdf.to_file(output_vector_path, driver="GeoJSON")
print(f"Vector data saved to {output_vector_path}")
