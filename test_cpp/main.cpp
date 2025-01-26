#include <opencv2/opencv.hpp>
#include <string>
#include <iostream>
#include <exception>

std::string path = "tiles/";

bool renderMapTiles(int minX, int maxX, int minY, int maxY, std::string saveAs) {
    // Determine the size of the resulting image
    int width = (maxX - minX + 1) * 256;
    int height = (maxY - minY + 1) * 256;

    // Create a blank canvas for the combined image
    cv::Mat combinedImage(height, width, CV_8UC1, cv::Scalar(0));

    bool done = 1;

    // Iterate through the tiles in the bounding box
    for (int x = minX; x <= maxX; ++x) {
        for (int y = minY; y <= maxY; ++y) {
            try {
                // Read the tile image
                cv::Mat tileImage = cv::imread(path + std::to_string(x) + "/" + std::to_string(y) + ".png", cv::IMREAD_GRAYSCALE);
                if (tileImage.empty()) {
                    throw std::runtime_error("Image not found or invalid.");
                }

                // Convert the image to binary
                cv::threshold(tileImage, tileImage, 215, 255, cv::THRESH_BINARY_INV);

                // Calculate the position to place this tile in the final image
                int offsetX = (x - minX) * 256;
                int offsetY = (y - minY) * 256;

                // Paste the tile onto the canvas
                tileImage.copyTo(combinedImage(cv::Rect(offsetX, offsetY, 256, 256)));
            } catch (const std::exception& e) {
                done = 0;
                std::cerr << "Failed to fetch: " << path + std::to_string(x) + "/" + std::to_string(y) + ".png"<< std::endl;
            }
        }
    }

    if(done)
    cv::imwrite(saveAs,combinedImage);

    return !done;
}


int main() {
    int minX=187144;
    int maxX=187149;
    int minY=122959;
    int maxY=122960;

    renderMapTiles(minX, maxX, minY, maxY,"hello.bmp");

    return 0;
}
