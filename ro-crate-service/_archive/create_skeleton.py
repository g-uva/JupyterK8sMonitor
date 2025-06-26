import os
import uuid
import json

base_directory = "/home/jovyan/" # This only workks in the JupyterLab environment.
skeleton_structure = ""
with open("./skeleton.json", "r") as f:
    skeleton_structure = json.load(f)

def create_folders(base_path, structure):
     for name, subdirs in structure.items():
          if name == "":
               continue
          path = os.path.join(base_path, name)
          os.makedirs(path, exist_ok=True)
          create_folders(path, subdirs)

def main():
    unique_id = os.getenv("SESSION_ID")
    if not unique_id:
        print("No SESSION_ID found. Please execute generate_session_id.py script.")
    else:
        start_dir = "/home/jovyan/experiments-export/"
        os.makedirs(start_dir, exist_ok=True)
        root_key = list(skeleton_structure.keys())[0]
        base_dir = root_key.replace("<id>", unique_id)
        create_folders(start_dir, {base_dir: skeleton_structure[root_key]})
        print(f"Folder structure created under: {base_dir}")

if __name__ == "__main__":
    main()
