import os
from PIL import Image

def update_yolo_coordinates(input_file, output_file, crop_top, crop_bottom, original_height):
    """
    Updates YOLO label coordinates for a cropped image.

    Args:
        input_file (str): Path to the input YOLO label file.
        output_file (str): Path to save the updated YOLO label file.
        crop_top (int): Number of pixels cropped from the top.
        crop_bottom (int): Number of pixels cropped from the bottom.
        original_height (int): Original height of the image.
    """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            parts = line.strip().split()
            if len(parts) < 3 or len(parts) % 2 != 1:
                print(f"Skipping invalid line in {input_file}: {line.strip()}")
                continue

            class_id = parts[0]
            coordinates = [float(coord) for coord in parts[1:]]

            # Group into (x, y) pairs
            polygon_coords = [(coordinates[i], coordinates[i + 1]) for i in range(0, len(coordinates), 2)]

            # Adjust y-coordinates based on the crop
            updated_coords = []
            for x, y in polygon_coords:
                new_y = (y * original_height - crop_top) / (original_height - crop_top - crop_bottom)
                updated_coords.append((x, new_y))

            # Write updated coordinates to the output file
            updated_line = class_id + " " + " ".join(f"{x:.6f} {y:.6f}" for x, y in updated_coords)
            outfile.write(updated_line + "\n")

    print(f"Updated labels saved to '{output_file}'.")

def process_directory(image_dir, label_dir, output_image_dir, output_label_dir):
    """
    Processes a directory of images and labels to resize and update YOLO coordinates.

    Args:
        image_dir (str): Path to the directory containing images.
        label_dir (str): Path to the directory containing YOLO label files.
        output_image_dir (str): Path to save the resized images.
        output_label_dir (str): Path to save the updated label files.
    """
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    if not os.path.exists(output_label_dir):
        os.makedirs(output_label_dir)

    crop_top = 100
    crop_bottom = 100
    original_height = 800

    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(image_dir, filename)
            label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + ".txt")
            output_image_path = os.path.join(output_image_dir, filename)
            output_label_path = os.path.join(output_label_dir, os.path.splitext(filename)[0] + ".txt")

            # Process image
            with Image.open(image_path) as img:
                if img.size != (800, 800):
                    print(f"Skipping non-800x800 image: {filename}")
                    continue

                cropped_img = img.crop((0, crop_top, 800, original_height - crop_bottom))
                cropped_img.save(output_image_path)

            # Process label
            if os.path.exists(label_path):
                update_yolo_coordinates(label_path, output_label_path, crop_top, crop_bottom, original_height)

    print("Processing complete.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print("Usage: python crop__data_800x800_to_800x600.py <image_dir> <label_dir> <output_image_dir> <output_label_dir>")
        sys.exit(1)

    image_dir = sys.argv[1]
    label_dir = sys.argv[2]
    output_image_dir = sys.argv[3]
    output_label_dir = sys.argv[4]

    process_directory(image_dir, label_dir, output_image_dir, output_label_dir)
