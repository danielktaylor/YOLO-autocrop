import argparse
import os
import re
import sys
from PIL import Image
from PIL import ImageDraw

def main():
    image_dir = "./images"
    label_dir = "./labels"
    preview_dir = "./previews"

    # Ensure directories exist
    if not os.path.exists(image_dir):
        print("missing image dir")
        sys.exit(1)
    if not os.path.exists(label_dir):
        print("missing label dir")
        sys.exit(1)
    if not os.path.exists(preview_dir):
        print("missing preview dir")
        sys.exit(1)

    # Get a list of files in each directory
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
    
    for image_file in image_files:
        img = Image.open(os.path.join(image_dir, image_file)).convert('RGBA')
        width = img.size[0]
        height = img.size[1]

        label_file = os.path.join(label_dir, re.sub(r'\.(jpeg|jpg|JPEG|JPG)$', '.txt', image_file))

        # YOLOv11 labels file format:
        # https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats
        with open(label_file) as polygons:
            for line in polygons:
                x = []
                y = []

                points = line.split()[1:]
                x = points[::2] # all even indexes
                y = points[1::2] # all odd indexes

                # Convert from percentages to actual pixel values
                x = [float(pt) * width for pt in x]
                y = [float(pt) * height for pt in y]

                # convert values to ints
                x = map(int, x)
                y = map(int, y)

                img2 = img.copy()
                draw = ImageDraw.Draw(img2)
                draw.polygon(list(zip(x,y)), fill = "green")

                img3 = Image.blend(img, img2, 0.5)
                img = img3

            img.save(os.path.join(preview_dir, 'preview_' + image_file + ".png"))

if __name__ == "__main__":
    main()
