from PIL import Image
from PIL import ImageDraw
img = Image.open('in.jpg').convert('RGBA')

width = img.size[0]
height = img.size[1]

x = []
y = []

# YOLOv11 labels file format:
# https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats
with open('polygons.txt') as polygons:
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
img3.save('out.png')
