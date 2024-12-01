import argparse
from PIL import Image
from PIL import ImageDraw

def parse_args():
    parser = argparse.ArgumentParser(description="Preview the polygons drawn by YOLOv11 labels.")
    parser.add_argument("image", type=str, help="Input image.")
    parser.add_argument("labels", type=str, help="Input file with labels.")
    return parser.parse_args()
		
def main():
    args = parse_args()

    img = Image.open(args.image).convert('RGBA')
    width = img.size[0]
    height = img.size[1]

    x = []
    y = []

    # YOLOv11 labels file format:
    # https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats
    with open(args.labels) as polygons:
        for line in polygons:
            points = line.split()[1:]
            x = points[::2] # all even indexes
            y = points[1::2] # all odd indexes
            break # we are only supporting a single label right now

    # Convert from percentages to actual pixel values
    x = [float(pt) * width for pt in x]
    y = [float(pt) * height for pt in y]

    # convert values to ints
    x = map(int, x)
    y = map(int, y)

    img2 = img.copy()
    draw = ImageDraw.Draw(img2)
    draw.polygon(list(zip(x,y)), fill = "wheat")

    img3 = Image.blend(img, img2, 0.5)
    img3.save('preview.png')

if __name__ == "__main__":
    main()