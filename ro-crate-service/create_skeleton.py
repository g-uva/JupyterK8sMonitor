import os
import json
import uuid

base_directory = "/home/jovyan/" # This only workks in the JupyterLab environment.
skeleton_structure = {
    "ri_site_container_<id>-experiment": {
        "data": {
            "output": {
                "workflow_output_files": {}
            },
            "input": {
                "workflow_input_files": {}
            },
            "logs": {}
        },
        "executed": {},
        "environment": {},
        "": {}
    }
}

def create_folders(base_path, structure):
     for name, subdirs in structure.items():
          if name == "":
               continue
          path = os.path.join(base_path, name)
          os.makedirs(path, exist_ok=True)
          create_folders(path, subdirs)

def main():
    unique_id = uuid.uuid4().hex[:8]
    root_key = list(skeleton_structure.keys())[0]
    base_dir = root_key.replace("<id>", unique_id)
    create_folders(".", {base_dir: skeleton_structure[root_key]})
    print(f"Folder structure created under: {base_dir}")

if __name__ == "__main__":
    main()
