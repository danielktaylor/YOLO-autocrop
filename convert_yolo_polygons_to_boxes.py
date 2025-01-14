import os
import argparse

# Function to calculate bounding box from polygon coordinates
def polygon_to_bbox(polygon):
    # Extract x and y coordinates from the polygon
    x_coords = polygon[0::2]
    y_coords = polygon[1::2]

    # Calculate min and max for x and y
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    # Calculate center_x, center_y, width, and height
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min

    return center_x, center_y, width, height

# Main function to process files
def convert_yolo_polygon_to_bbox(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_file_path = os.path.join(input_dir, filename)
            output_file_path = os.path.join(output_dir, filename)

            with open(input_file_path, "r") as infile, open(output_file_path, "w") as outfile:
                for line in infile:
                    parts = line.strip().split()
                    class_id = parts[0]
                    polygon = list(map(float, parts[1:]))

                    # Convert polygon to bounding box
                    center_x, center_y, width, height = polygon_to_bbox(polygon)

                    # Write to the new file in YOLO format
                    outfile.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YOLO polygon annotations to bounding box format.")
    parser.add_argument("input_dir", type=str, help="Path to the input directory containing YOLO polygon files.")
    parser.add_argument("output_dir", type=str, help="Path to the output directory to save bounding box files.")

    args = parser.parse_args()

    convert_yolo_polygon_to_bbox(args.input_dir, args.output_dir)