
from PIL import Image
import mercantile
import requests
from io import BytesIO
import cv2
import numpy as np
import crop_image
import os
import sys
sys.path.append('/usr/lib/python3/dist-packages')
from osgeo import gdal, osr

def render_map_tiles(base_url, ne_lat, ne_lon, sw_lat, sw_lon, zoom_level):
    """
    Combines raster map tiles into a single rendered image based on the bounding box and zoom level.

    Args:
        base_url (str): Base URL to fetch map tiles, formatted as "http://example.com/{z}/{x}/{y}.png".
        ne_lat (float): Latitude of the northeast corner.
        ne_lon (float): Longitude of the northeast corner.
        sw_lat (float): Latitude of the southwest corner.
        sw_lon (float): Longitude of the southwest corner.
        zoom_level (int): Zoom level of the tiles.

    Returns:
        np.ndarray: Combined image of the specified bounding box as a NumPy array (OpenCV image format).
    """
    # Determine tile bounds based on the bounding box
    top_left_tile = mercantile.tile(sw_lon, ne_lat, zoom_level)
    bottom_right_tile = mercantile.tile(ne_lon, sw_lat, zoom_level)

    min_x = top_left_tile.x
    max_x = bottom_right_tile.x
    min_y = top_left_tile.y
    max_y = bottom_right_tile.y

    # Determine the size of the resulting image
    width = (max_x - min_x + 1) * 256
    height = (max_y - min_y + 1) * 256

    # Create a blank canvas for the combined image
    combined_image = np.zeros((height, width), dtype=np.uint8)

    # Iterate through the tiles in the bounding box
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            tile_url = base_url.format(z=zoom_level, x=x, y=y)
            try:
                print(tile_url)
                response = requests.get(tile_url)
                if response.status_code == 200:
                    # Read the image as a NumPy array
                    tile_image_ = np.asarray(bytearray(response.content), dtype=np.uint8)
                    tile_image = cv2.imdecode(tile_image_, cv2.IMREAD_GRAYSCALE)
                    tile_image_ = cv2.imdecode(tile_image_, cv2.IMREAD_UNCHANGED)
                    if not os.path.exists(str(x)):
                        os.makedirs(str(x))
                    cv2.imwrite(str(x)+'/'+str(y)+'.png',tile_image_)

                    # Convert the image to binary (1 byte per pixel)
                    _, tile_image = cv2.threshold(tile_image, 215, 255, cv2.THRESH_BINARY_INV)

                    # Calculate the position to place this tile in the final image
                    offset_x = (x - min_x) * 256
                    offset_y = (y - min_y) * 256

                    # Paste the tile onto the canvas
                    if tile_image is not None:
                        combined_image[offset_y:offset_y+256, offset_x:offset_x+256] = tile_image
            except Exception as e:
                print(f"Failed to fetch tile at {tile_url}: {e}")

    return combined_image



def render(ne_latitude,ne_longitude,sw_latitude,sw_longitude,image_name):
    base_url = "https://s3.ap-south-2.amazonaws.com/prod-assets.mypropertyqr.in/survey_border/{x}/{y}.png"
    # Define the bounding box and zoom level
    ne_latitude = 11.07124
    ne_longitude = 77.011059
    sw_latitude = 11.070540
    sw_longitude = 77.004476
    zoom = 18
    # Generate the combined image
    rendered_image = render_map_tiles(base_url, ne_latitude, ne_longitude, sw_latitude, sw_longitude, zoom)

    rendered_image = crop_image.crop(rendered_image, ne_latitude, ne_longitude, sw_latitude, sw_longitude)


    # Georeference settings from the provided variables
    height, width = rendered_image.shape
    pixel_width = (ne_longitude - sw_longitude) / width
    pixel_height = (ne_latitude - sw_latitude) / height

    sv_dir = "raster/"+image_name

    if not os.path.exists(sv_dir):
       os.makedirs(sv_dir)

    # Create GDAL raster
    driver = gdal.GetDriverByName("BMP")
    dataset = driver.Create(sv_dir+'/'+image_name+".bmp", width, height, 1, gdal.GDT_Byte)
    dataset.GetRasterBand(1).WriteArray(rendered_image)
    dataset.SetGeoTransform([sw_longitude, pixel_width, 0, ne_latitude, 0, -pixel_height])

    # Set spatial reference (WGS 84)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    dataset.SetProjection(srs.ExportToWkt())
    dataset.FlushCache()
