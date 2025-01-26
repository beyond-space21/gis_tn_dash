import cv2
from pyproj import Transformer
import math

transformer_to_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857")
def convert_4326_to_3857(lat, lon):
    x, y = transformer_to_3857.transform(lat, lon)
    return {'x': x, 'y': y}

def get_tile_coordinates(lat, lon, zoom):
    coords = convert_4326_to_3857(lat, lon)
    x, y = coords['x'], coords['y']

    tile_size = 256  # Size of each tile in pixels
    initial_resolution = 2 * math.pi * 6378137 / tile_size  # Resolution at zoom level 0
    resolution = initial_resolution / (2 ** zoom)

    tile_x = math.floor((x + 20037508.3427892) / (resolution * tile_size))
    tile_y = math.floor((20037508.3427892 - y) / (resolution * tile_size))

    pixel_x = math.floor(((x + 20037508.3427892) % (resolution * tile_size)) / resolution)
    pixel_y = math.floor(((20037508.3427892 - y) % (resolution * tile_size)) / resolution)

    return {
        "tx":tile_x,
        "ty":tile_y,
        "pix_cord_X":pixel_x,
        "pix_cord_Y":pixel_y
    }

def crop_image(image, top, right, bottom, left):
    """
    Crops the image based on the provided top, right, bottom, and left values.

    Args:
        image (numpy.ndarray): The input image.
        top (int): The number of pixels to crop from the top.
        right (int): The number of pixels to crop from the right.
        bottom (int): The number of pixels to crop from the bottom.
        left (int): The number of pixels to crop from the left.

    Returns:
        numpy.ndarray: The cropped image.
    """
    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Calculate the new boundaries
    start_y = top
    end_y = height - bottom
    start_x = left
    end_x = width - right

    # Crop the image
    cropped_image = image[start_y:end_y, start_x:end_x]

    return cropped_image

def crop(image, ne_latitude, ne_longitude, sw_latitude, sw_longitude):
    ne = get_tile_coordinates(ne_latitude,ne_longitude,18)
    sw = get_tile_coordinates(sw_latitude,sw_longitude,18)

    print(ne)
    print(sw)
    print()

    tp_crp = (ne['pix_cord_Y'])
    bt_crp = (256-sw['pix_cord_Y'])
    rt_crp = (256-ne['pix_cord_X'])
    lt_crp = (sw['pix_cord_X'])
    
    print("     ",tp_crp)
    print(lt_crp,"      ",rt_crp)
    print("     ",bt_crp)

    return crop_image(image,tp_crp,rt_crp,bt_crp,lt_crp)