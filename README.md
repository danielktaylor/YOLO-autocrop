# YOLOv11 Autocrop

Automatically crop images to a desired width:height ratio, resize the images,  and update the polygon points to match. Tries to preserve labeled objects by when choosing which sides to crop from.

This is useful if you have training data from a camera that uses a different image size ratio than the live production cameras.

## Usage

`autocrop.py <width> <height>`

Output debug images by including `--debug` flag.

Preview individual image polygons with `preview.py <image> <labels>`