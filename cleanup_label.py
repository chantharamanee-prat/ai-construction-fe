import os

labels_dir = "server/datasets/labels"

for filename in os.listdir(labels_dir):
    file_path = os.path.join(labels_dir, filename)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
        # Remove the first line if it contains '# progress:'
        if lines and lines[0].startswith("# progress:"):
            lines = lines[1:]
            with open(file_path, "w") as f:
                f.writelines(lines)