import cv2
import numpy as np

def zhang_suen_thinning(binary_image):
    size = np.size(binary_image)
    skeleton = np.zeros(binary_image.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        open_img = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(binary_image, open_img)
        eroded = cv2.erode(binary_image, element)
        skeleton = cv2.bitwise_or(skeleton, temp)
        binary_image = eroded.copy()
        if cv2.countNonZero(binary_image) == 0:
            break
    return skeleton

# Load and thin a binary raster image
input_image = cv2.imread("rs_cd/combined_image_b.png", cv2.IMREAD_GRAYSCALE)
_, binary_image = cv2.threshold(input_image, 127, 255, cv2.THRESH_BINARY)
thinned_image = zhang_suen_thinning(binary_image)
cv2.imwrite("thinned_raster.png", thinned_image)
