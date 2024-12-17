import os
import shutil

image_dir="./images"
label_dir="./labels"

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
            try:
                # Read the first character (class integer) from the label file
                with open(label_path, "r") as lf:
                    first_line = lf.readline().strip()
                    class_id = first_line.split(" ")[0]  # Take the first "word"
                    
                    # Ensure the class_id is an integer
                    if class_id.isdigit():
                        target_dir = os.path.join(image_dir, class_id)
                        os.makedirs(target_dir, exist_ok=True)
            except Exception as e:
                print(f"Error reading label file {label_file}: {e}")

        # Move the image file to the appropriate directory
        try:
            shutil.move(image_path, os.path.join(target_dir, image_file))
        except Exception as e:
            print(f"Error moving file {image_file}: {e}")

    print("Image organization complete.")

if __name__ == "__main__":
    organize_images()