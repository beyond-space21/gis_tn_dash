def render_map_tiles(path,min_x,max_x,min_y,max_y):


    # Determine the size of the resulting image
    width = (max_x - min_x + 1) * 256
    height = (max_y - min_y + 1) * 256

    # Create a blank canvas for the combined image
    combined_image = np.zeros((height, width), dtype=np.uint8)

    # Iterate through the tiles in the bounding box
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            tile_url = path.format(x=x, y=y)
            try:
                    tile_image = cv2.imread(path)
                    tile_image = cv2.imdecode(tile_image, cv2.IMREAD_GRAYSCALE)

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