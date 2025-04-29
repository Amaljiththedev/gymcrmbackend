import os

def print_tree(directory, prefix=""):
    entries = sorted(os.listdir(directory))
    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)

print_tree(".")
