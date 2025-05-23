#!/bin/bash

INPUT_DIR="/home/jovyan/input"
TARGET_DIR="/home/jovyan/experiments-export/ri_site_container_$SESSION_ID-experiment/data/input/"

if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: Folder '$INPUT_DIR' does not exist."
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Target folder '$TARGET_DIR' does not exist."
  exit 1
fi

# sudo rm -rf "$TARGET_DIR"/ 2>/dev/null
cp "$INPUT_DIR"/* "$TARGET_DIR"/ 2>/dev/null

if [ $? -ne 0 ]; then
  echo "Warning: No files moved. 'input/' may be empty, or there was an error."
else
  echo "All files from '$INPUT_DIR' moved to '$TARGET_DIR'"
fi

# echo "=== OS Detection ==="
# uname_str="$(uname -s)"
# case "${uname_str}" in
#     Linux*)     os=Linux;;
#     Darwin*)    os=Mac;;
#     CYGWIN*|MINGW*|MSYS*)    os=Windows;;
#     *)          os="UNKNOWN:${uname_str}"
# esac
# echo "Detected OS: $os"
# echo "$os" > os_info.txt

# config_files=()

echo "=== OS Detection ==="
uname_str="$(uname -s)"
os_info=""

case "${uname_str}" in
    Linux*)
        os="Linux"
        if [ -f /etc/os-release ]; then
            # Parse common distro info
            . /etc/os-release
            os_info="Linux ($NAME $VERSION)"
        else
            os_info="Linux (Unknown distro)"
        fi
        ;;
    Darwin*)
        os="Mac"
        # Use sw_vers for macOS version info
        if command -v sw_vers &>/dev/null; then
            product_name=$(sw_vers -productName)
            product_version=$(sw_vers -productVersion)
            os_info="Mac ($product_name $product_version)"
        else
            os_info="Mac (Unknown version)"
        fi
        ;;
    CYGWIN*|MINGW*|MSYS*)
        os="Windows"
        # Try to get Windows version info
        if command -v cmd.exe &>/dev/null; then
            win_ver=$(cmd.exe /c ver | tr -d '\r')
            os_info="Windows ($win_ver)"
        else
            os_info="Windows (Unknown version)"
        fi
        ;;
    *)
        os="UNKNOWN:${uname_str}"
        os_info="Unknown OS"
        ;;
esac

echo "Detected OS: $os_info"
echo "$os_info" > os_info.txt

# 1. Kubernetes config
if [ -f "$HOME/.kube/config" ]; then
    echo "Kubernetes config found at $HOME/.kube/config"
    config_files+=("$HOME/.kube/config")
else
    echo "Kubernetes config NOT found"
fi

# 2. Dockerfile at /home/jovyan/
if [ -f "/home/jovyan/Dockerfile" ]; then
    echo "Dockerfile found at /home/jovyan/Dockerfile"
    config_files+=("/home/jovyan/Dockerfile")
else
    echo "Dockerfile NOT found at /home/jovyan/"
fi

# 3. Ansible or CloudFormation file at /home/jovyan/
ansible_files=$(ls /home/jovyan/*.yml /home/jovyan/*.yaml 2>/dev/null)
if [ ! -z "$ansible_files" ]; then
    echo "Ansible/CloudFormation config file(s) found:"
    for file in $ansible_files; do
        echo "$file"
        config_files+=("$file")
    done
else
    echo "No Ansible or CloudFormation config file found at /home/jovyan/"
fi

# Create the TARGET_DIR if it does not exist
mkdir -p "$TARGET_DIR"

# Move os_info.txt and all detected config files to the TARGET_DIR
echo "Moving os_info.txt and config files to $TARGET_DIR ..."
mv os_info.txt "$TARGET_DIR"/

for file in "${config_files[@]}"; do
    # Copy instead of move if you prefer: use cp instead of mv
    cp "$file" "$TARGET_DIR"/
done

echo "Done."