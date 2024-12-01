import argparse
import os
from PIL import Image
from PIL import ImageDraw
from pathlib import Path    

def parse_args():
    parser = argparse.ArgumentParser(description="Autocrop and resize images, adjusting YOLOv11 labels.")
    parser.add_argument("width", type=int, help="Target width of the cropped/resized image.")
    parser.add_argument("height", type=int, help="Target height of the cropped/resized image.")
    parser.add_argument("--debug", help="Output preview images for debugging.", action="store_true")
    return parser.parse_args()

def load_label(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        objects = []
        for line in lines:
            parts = line.strip().split()
            class_index = int(parts[0])
            points = list(map(float, parts[1:]))
            objects.append((class_index, points))
        return objects

def save_label(file_path, objects):
    with open(file_path, 'w') as file:
        for i, obj in enumerate(objects):
            class_index, points = obj
            points_str = ' '.join(map(lambda x: f"{x:.16f}", points))
            # Add a newline for all but the last object
            if i < len(objects) - 1:
                file.write(f"{class_index} {points_str}\n")
            else:
                file.write(f"{class_index} {points_str}")

def generate_debug_image(image, labels, output_path, orig_image):
    img = Image.open(image).convert('RGBA')
    width = img.size[0]
    height = img.size[1]

    x = []
    y = []

    # YOLOv11 labels file format:
    # https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats
    with open(labels) as polygons:
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

    polygon_image = img.copy()
    draw = ImageDraw.Draw(polygon_image)
    draw.polygon(list(zip(x,y)), fill = "wheat")

    lower_image = Image.blend(img, polygon_image, 0.5)
    upper_image = Image.open(orig_image).convert('RGBA')

    # Calculate the width and height of the new image
    width = max(lower_image.width, upper_image.width)
    height = lower_image.height + upper_image.height
    
    # Create a new blank image with the calculated dimensions
    final_image = Image.new("RGB", (width, height), (255, 255, 255))  # White background
    final_image.paste(upper_image, (0, 0))
    final_image.paste(lower_image, (0, upper_image.height))
    final_image.save(os.path.join(output_path, Path(image).stem + ".png"))

def adjust_polygon(polygon, orig_width, orig_height, crop_x, crop_y, crop_width, crop_height, target_width, target_height):
    adjusted = []
    scale_x = target_width / crop_width
    scale_y = target_height / crop_height

    for i in range(0, len(polygon), 2):
        x = polygon[i] * orig_width - crop_x
        y = polygon[i + 1] * orig_height - crop_y
        x = max(0, min(x, crop_width)) * scale_x / target_width
        y = max(0, min(y, crop_height)) * scale_y / target_height
        adjusted.extend([x, y])

    return adjusted

# TODO this doesn't work correctly
def process_image(image_path, label_path, output_image_path, output_label_path, target_width, target_height):
    image = Image.open(image_path)
    orig_width, orig_height = image.size

    objects = load_label(label_path)

    # Calculate target aspect ratio
    target_aspect_ratio = target_width / target_height
    orig_aspect_ratio = orig_width / orig_height

    if orig_aspect_ratio > target_aspect_ratio:
        # Wider than target, crop width
        new_width = int(orig_height * target_aspect_ratio)
        crop_x = (orig_width - new_width) // 2
        crop_y = 0
        crop_width = new_width
        crop_height = orig_height
    else:
        # Taller than target, crop height
        new_height = int(orig_width / target_aspect_ratio)
        crop_x = 0
        crop_y = (orig_height - new_height) // 2
        crop_width = orig_width
        crop_height = new_height

    # Adjust crop box to preserve maximum objects
    for class_index, points in objects:
        for i in range(0, len(points), 2):
            x = points[i] * orig_width
            y = points[i + 1] * orig_height
            crop_x = max(0, min(crop_x, int(x - crop_width / 2)))
            crop_y = max(0, min(crop_y, int(y - crop_height / 2)))

    # Crop the image
    cropped_image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))

    # Resize the image
    resized_image = cropped_image.resize((target_width, target_height))

    # Adjust the labels
    adjusted_objects = []
    for class_index, points in objects:
        adjusted_points = adjust_polygon(points, orig_width, orig_height, crop_x, crop_y, crop_width, crop_height, target_width, target_height)
        adjusted_objects.append((class_index, adjusted_points))

    # Save the processed image and labels
    resized_image.save(output_image_path, "JPEG")
    save_label(output_label_path, adjusted_objects)

def main():
    args = parse_args()

    input_images_dir = "./input/images"
    input_labels_dir = "./input/labels"
    output_images_dir = "./output/images"
    output_labels_dir = "./output/labels"
    output_debug_dir = "./output/debug"

    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_labels_dir, exist_ok=True)
    if args.debug:
        os.makedirs(output_debug_dir, exist_ok=True)

    for image_filename in os.listdir(input_images_dir):
        if image_filename.lower().endswith(".jpg") or image_filename.lower().endswith(".jpeg"):
            base_name = os.path.splitext(image_filename)[0]
            label_filename = f"{base_name}.txt"

            image_path = os.path.join(input_images_dir, image_filename)
            label_path = os.path.join(input_labels_dir, label_filename)

            if not os.path.exists(label_path):
                print(f"Warning: Label file {label_filename} does not exist for image {image_filename}. Skipping.")
                continue

            output_image_path = os.path.join(output_images_dir, image_filename)
            output_label_path = os.path.join(output_labels_dir, label_filename)

            process_image(image_path, label_path, output_image_path, output_label_path, args.width, args.height)

            if args.debug:
                generate_debug_image(output_image_path, output_label_path, output_debug_dir, image_path)

if __name__ == "__main__":
    main()
