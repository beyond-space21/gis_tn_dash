import sys
sys.path.append('/usr/lib/python3/dist-packages')

import cv2
from osgeo import gdal, osr

import importlib
import numpy as np

# Load binary image (grayscale)
binary_image = cv2.imread("combined_image_b.bmp", cv2.IMREAD_GRAYSCALE)

# Georeference settings
upper_left_x, upper_left_y = 77.004476, 11.07124
lower_right_x, lower_right_y = 77.011059, 11.070540
height, width = binary_image.shape
pixel_width = (lower_right_x - upper_left_x) / width
pixel_height = (upper_left_y - lower_right_y) / height

# Create GDAL raster
driver = gdal.GetDriverByName("BMP")
dataset = driver.Create("binary_image_georeferenced.bmp", width, height, 1, gdal.GDT_Byte)
dataset.GetRasterBand(1).WriteArray(binary_image)
dataset.SetGeoTransform([upper_left_x, pixel_width, 0, upper_left_y, 0, -pixel_height])

# Set spatial reference (WGS 84)
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
dataset.SetProjection(srs.ExportToWkt())
dataset.FlushCache()