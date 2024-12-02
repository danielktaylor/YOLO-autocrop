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

    # YOLO labels file format:
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

def adjust_polygon(polygon, orig_width, orig_height, crop_x, crop_y, cropped_width, cropped_height, target_width, target_height):
    adjusted = []
    scale_x = target_width / cropped_width
    scale_y = target_height / cropped_height

    for i in range(0, len(polygon), 2):
        x = polygon[i] * orig_width - crop_x
        y = polygon[i + 1] * orig_height - crop_y
        x = max(0, min(x, cropped_width)) * scale_x / target_width
        y = max(0, min(y, cropped_height)) * scale_y / target_height
        adjusted.extend([x, y])

    return adjusted

def calculate_crop(width, height, crop_x, crop_y, polygons):
    """
    Calculate the optimal cropping strategy to minimize the area of polygons lost.

    Args:
        width (int): Current pixel width of the image.
        height (int): Current pixel height of the image.
        crop_x (int): Amount to crop horizontally, in total.
        crop_y (int): Amount to crop vertically, in total.
        polygons (list): List of polygons in YOLO format, where each polygon is a 
                        list of normalized (x, y) points.

    Returns:
        tuple: Optimal cropping amounts (left_crop, right_crop, top_crop, bottom_crop).
    """

    # Convert normalized polygons to absolute pixel coordinates
    absolute_polygons = [
        [(x * width, y * height) for x, y in zip(poly[::2], poly[1::2])]
        for poly in polygons
    ]

    def crop_loss(left, right, top, bottom):
        """Calculate the loss of polygon area for a given crop."""
        cropped_area = 0
        for polygon in absolute_polygons:
            cropped_polygon = [
                (max(left, min(x, width - right)), max(top, min(y, height - bottom)))
                for x, y in polygon
            ]

            # Calculate polygon area before and after cropping
            original_area = polygon_area(polygon)
            remaining_area = polygon_area(cropped_polygon)
            cropped_area += original_area - remaining_area
        return cropped_area

    def polygon_area(polygon):
        """Calculate the area of a polygon using the Shoelace formula."""
        if len(polygon) < 3:
            return 0  # Not a valid polygon
        x_coords, y_coords = zip(*polygon)
        return abs(
            sum(x_coords[i] * y_coords[i - 1] - y_coords[i] * x_coords[i - 1] for i in range(len(polygon)))
        ) / 2

    # Check for easy solution: full crop from one side
    if crop_loss(crop_x, 0, crop_y, 0) == 0:
        return (crop_x, 0, crop_y, 0)
    if crop_loss(0, crop_x, crop_y, 0) == 0:
        return (0, crop_x, crop_y, 0)
    if crop_loss(crop_x, 0, 0, crop_y) == 0:
        return (crop_x, 0, 0, crop_y)
    if crop_loss(0, crop_x, 0, crop_y) == 0:
        return (0, crop_x, 0, crop_y)

    # Try different cropping splits
    best_loss = float('inf')
    best_crop = (0, 0, 0, 0)

    for left in range(0, crop_x + 1):
        right = crop_x - left
        for top in range(0, crop_y + 1):
            bottom = crop_y - top
            loss = crop_loss(left, right, top, bottom)
            if loss == 0:
                return (left, right, top, bottom)  # Stop early if no loss
            if loss < best_loss:
                best_loss = loss
                best_crop = (left, right, top, bottom)

    return best_crop

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
        cropped_width = new_width
        cropped_height = orig_height
    else:
        # Taller than target, crop height
        new_height = int(orig_width / target_aspect_ratio)
        crop_x = 0
        crop_y = (orig_height - new_height) // 2
        cropped_width = orig_width
        cropped_height = new_height

    crop_left, crop_right, crop_top, crop_bottom = calculate_crop(orig_width, orig_height, crop_x*2, crop_y*2, [lst for _, lst in objects])
    cropped_image = image.crop((crop_left, crop_top, cropped_width - crop_right, cropped_height - crop_bottom))

    # Resize the image
    resized_image = cropped_image.resize((target_width, target_height))

    # Adjust the labels
    adjusted_objects = []
    for class_index, points in objects:
        adjusted_points = adjust_polygon(points, orig_width, orig_height, crop_x, crop_y, cropped_width, cropped_height, target_width, target_height)
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
