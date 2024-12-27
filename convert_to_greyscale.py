from PIL import Image
import os

# Input and output directories
input_dir = "./images"
output_dir = "./greyscale"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process all image files in the input directory
for filename in os.listdir(input_dir):
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Open the image
        with Image.open(input_path) as img:
            # Ensure the image is in RGB mode
            img = img.convert("RGB")

            # Extract the greyscale intensity
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    gray = int(0.299 * r + 0.587 * g + 0.114 * b)  # Standard greyscale formula
                    pixels[x, y] = (gray, gray, gray)  # Set RGB channels to the same value

            # Save the result
            img.save(output_path)

print(f"Processed images saved to {output_dir}")