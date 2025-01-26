## Directoy reference
```
root_folder
    |_app_files
    |_grassdb/{id}/
    |_shp/{id}
    |_raster/{id}/
    |_logs/{id}/
```

## Common reference

gdalinfo rs_cd/crp.png

gdal_translate -a_ullr 77.004476 11.07124 77.011059 11.070540 -a_srs EPSG:4326 combined_image_b.bmp combined_image_b_.bmp

sudo apt-get install python3-gdal
