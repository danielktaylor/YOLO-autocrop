from PIL import Image, ImageDraw
import shutil
import sys
import os

image_dir="./images"
label_dir="./labels"

def yolo_to_pixel_coordinates(polygon_coords, image_width, image_height):
    """
    Converts YOLO normalized coordinates to pixel coordinates.
    
    Args:
        polygon_coords (list): List of (x, y) normalized coordinates.
        image_width (int): Width of the image in pixels.
        image_height (int): Height of the image in pixels.

    Returns:
        list: List of (x, y) pixel coordinates.
    """
    return [
        (int(x * image_width), int(y * image_height))
        for x, y in polygon_coords
    ]

def crop_polygon(image_filename, yolo_coords):
    """
    Crops an image around a polygon defined by YOLO coordinates.
    
    Args:
        image_filename (str): Path to the image file.
        yolo_coords (str): YOLO polygon coordinates as a string.
    
    Returns:
        PIL.Image: Cropped image.
    """
    # Load the image
    image = Image.open(image_filename).convert("RGB")
    image_width, image_height = image.size

    # Parse YOLO coordinates
    coords = yolo_coords.split()
    polygon_coords = [(float(coords[i]), float(coords[i + 1])) for i in range(1, len(coords), 2)]

    # Convert to pixel coordinates
    pixel_coords = yolo_to_pixel_coordinates(polygon_coords, image_width, image_height)

    # Determine the bounding box of the polygon
    x_coords, y_coords = zip(*pixel_coords)
    bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # Expand the bounding box slightly (optional, for padding)
    padding = 0  # Adjust padding as needed
    bbox = (
        max(bbox[0] - padding, 0),
        max(bbox[1] - padding, 0),
        min(bbox[2] + padding, image_width),
        min(bbox[3] + padding, image_height)
    )

    # Crop the image to the bounding box
    cropped_image = image.crop(bbox)

    return cropped_image

# TODO not sure if I need to add padding?
def crop_polygon_with_padding(image_filename, yolo_coords):
    """
    Crops an image around a polygon defined by YOLO coordinates.
    
    Args:
        image_filename (str): Path to the image file.
        yolo_coords (str): YOLO polygon coordinates as a string.
    
    Returns:
        PIL.Image: Cropped image.
    """
    # Load the image
    image = Image.open(image_filename).convert("RGB")
    image_width, image_height = image.size

    # Parse YOLO coordinates
    coords = yolo_coords.split()
    polygon_coords = [(float(coords[i]), float(coords[i + 1])) for i in range(1, len(coords), 2)]

    # Convert to pixel coordinates
    pixel_coords = yolo_to_pixel_coordinates(polygon_coords, image_width, image_height)

    # Determine the bounding box of the polygon
    x_coords, y_coords = zip(*pixel_coords)
    bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    # Expand the bounding box slightly (optional, for padding)
    padding = 10  # Adjust padding as needed
    bbox = (
        max(bbox[0] - padding, 0),
        max(bbox[1] - padding, 0),
        min(bbox[2] + padding, image_width),
        min(bbox[3] + padding, image_height)
    )

    # Crop the image to the bounding box
    cropped_image = image.crop(bbox)

    # Make the image square by adding black padding
    cropped_width, cropped_height = cropped_image.size
    if cropped_width != cropped_height:
        square_size = max(cropped_width, cropped_height)
        square_image = Image.new("RGB", (square_size, square_size), (0, 0, 0))
        paste_x = (square_size - cropped_width) // 2
        paste_y = (square_size - cropped_height) // 2
        square_image.paste(cropped_image, (paste_x, paste_y))
        return square_image

    return cropped_image

def organize_images():
    # Define the directory where images without a class will go
    no_class_dir = os.path.join(image_dir, "no_class")
    os.makedirs(no_class_dir, exist_ok=True)

    # List all files in the images directory
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)

        # Skip if not a file
        if not os.path.isfile(image_path):
            continue

        # Build the corresponding label file path
        label_file = os.path.splitext(image_file)[0] + ".txt"
        label_path = os.path.join(label_dir, label_file)

        # Default target directory for images with no class
        target_dir = no_class_dir

        # Check if the label file exists
        if os.path.exists(label_path):
            # Read the first character (class integer) from the label file
            with open(label_path, "r") as lf:
                first_line = lf.readline().strip()
                class_id = first_line.split(" ")[0]  # Take the first "word"
                
                # Ensure the class_id is an integer
                if class_id.isdigit():
                    target_dir = os.path.join(image_dir, class_id)
                    os.makedirs(target_dir, exist_ok=True)

                    dst = os.path.join(target_dir, image_file)
                    shutil.move(image_path, dst)

                    cropped_image = crop_polygon_with_padding(dst, first_line)
                    cropped_image.save(dst)

    print("Image organization complete.")

if __name__ == "__main__":
    organize_images()