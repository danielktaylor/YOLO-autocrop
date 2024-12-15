import os
import shutil

def find_unmatched_images(image_dir, text_dir, missing_dir):
    # Ensure the directories exist
    if not os.path.isdir(image_dir):
        print(f"Error: The directory {image_dir} does not exist.")
        return
    if not os.path.isdir(text_dir):
        print(f"Error: The directory {text_dir} does not exist.")
        return

    # Ensure the missing directory exists
    if not os.path.exists(missing_dir):
        os.makedirs(missing_dir)

    # Get a list of files in each directory
    image_files = os.listdir(image_dir)
    text_files = os.listdir(text_dir)

    # Create a set of text file names without the .txt extension
    text_file_basenames = {os.path.splitext(text_file)[0] for text_file in text_files if text_file.endswith('.txt')}

    # Find image files without a matching .txt file
    unmatched_images = []
    for image_file in image_files:
        #image_basename, _ = os.path.splitext(image_file)
        if image_file not in text_file_basenames:
            unmatched_images.append(image_file)

    # Move unmatched image files to the missing directory
    if unmatched_images:
        print("Image files without a matching .txt file (moved to missing directory):")
        for unmatched_image in unmatched_images:
            print(unmatched_image)
            source_path = os.path.join(image_dir, unmatched_image)
            destination_path = os.path.join(missing_dir, unmatched_image)
            shutil.move(source_path, destination_path)
    else:
        print("All image files have matching .txt files.")

if __name__ == "__main__":
    # Directories
    image_dir = "./images"
    text_dir = "./labels"
    missing_dir = "./missing"

    find_unmatched_images(image_dir, text_dir, missing_dir)
