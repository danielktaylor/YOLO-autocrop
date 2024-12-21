import os

def adjust_coordinates(input_folder, output_folder):
    """
    Adjusts YOLO label coordinates from 800x600 to 800x800 resolution.
    Black bars are added to the top and bottom, so y-coordinates need scaling.

    Parameters:
    - input_folder: Folder containing input .txt files.
    - output_folder: Folder to save adjusted .txt files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r") as infile:
                lines = infile.readlines()

            adjusted_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) > 1:
                    class_id = parts[0]
                    coords = list(map(float, parts[1:]))

                    # Adjust y-coordinates (odd indices in the coords list)
                    for i in range(1, len(coords), 2):
                        coords[i] = (coords[i] * 600 + 100) / 800

                    adjusted_line = f"{class_id} " + " ".join(map(str, coords))
                    adjusted_lines.append(adjusted_line)

            with open(output_path, "w") as outfile:
                outfile.write("\n".join(adjusted_lines) + "\n")

    print(f"Adjusted files saved to: {output_folder}")

# Example usage
input_folder = "./labels"
output_folder = "./new_labels"
adjust_coordinates(input_folder, output_folder)