#!/usr/bin/env python3
import os
import sys
import zipfile
from datetime import datetime

BASE_DIR = "/home/jovyan/export-metrics"
if not os.path.isdir(BASE_DIR):
    sys.exit(f"Error: ./{BASE_DIR}/ not found.")

timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
zip_name = f"{BASE_DIR}-{timestamp}.zip"

with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            # archive paths relative to BASE_DIR parent
            arcname = os.path.relpath(full_path, os.path.dirname(BASE_DIR))
            zf.write(full_path, arcname)
print(f"✔ Created archive: {zip_name}")

# If running in a Jupyter notebook, you can display a download link:
try:
    from IPython.display import FileLink, display
    display(FileLink(zip_name))
except ImportError:
    pass