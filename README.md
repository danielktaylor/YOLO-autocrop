# YOLO Autocrop

Automatically crop images to a desired width:height ratio, resize the images, and update the polygon points to match. Preserves the largest amount of labeled objects area possible when choosing which sides to crop from.

This script is useful if you have training data from a camera that uses a different image size ratio than the live production cameras.

## Usage

Expected directory structure:

- `./input/images`
	- All input images
- `./input/labels`
	- All label files in YOLO format, one per image, with `.txt` extension (see the [YOLO docs](https://docs.ultralytics.com/datasets/segment/#supported-dataset-formats))

`autocrop.py <width> <height>`

Output debug images by including `--debug` flag.

## Example

See `sample` directory.

This was generated using the following two commands (after moving the `input` directory to the project's root directory):

`python preview.py ./input/images/apples.jpg ./input/labels/apples.txt`

`python autocrop.py 300 400 --debug`

# Other utilities

* **preview.py**: Preview individual image polygons with `preview.py <image> <labels>`.
* **preview_all.py**: Draw polygons on an entire directory of images.
* **add_image_padding.sh**: Draw black bars around rectangular images to make them square.
* **adjust_labels_for_800x800.py**: Adjust polygon coordinates for 800x600 -> 800x800.
* **convert_dataset_for_classification.py**: Convert an object detection dataset to a classification dataset. Crops around objects and organizes files into the correct directory structure.
* **convert_to_greyscale.py**: Convert RGB images to greyscale, but keep the images as 3-channel RGB format.
* **find_missing_file_pairs.py**: Check if all image files have a matching .txt label file
* **organize_files_by_class.py**: Move files into folders based on their class (in .txt files)
