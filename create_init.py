import os

def create_init_files(base_path):
    """Walk through all folders and create __init__.py if missing."""
    for root, dirs, files in os.walk(base_path):
        # Skip hidden folders like .git, .venv
        if any(part.startswith('.') for part in root.split(os.sep)):
            continue
        
        # Create __init__.py if it's a Python module folder
        if "__init__.py" not in files:
            init_path = os.path.join(root, "__init__.py")
            open(init_path, 'w').close()
            print(f"Created: {init_path}")

if __name__ == "__main__":
    base_folder = "."  # You can set this to your main project folder
    create_init_files(base_folder)
