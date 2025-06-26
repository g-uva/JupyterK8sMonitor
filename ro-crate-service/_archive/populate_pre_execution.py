import os
import shutil
import platform
import json
from kubernetes import config, client
from pathlib import Path

BASE_DIR = "/home/jovyan/experiments-export"

def get_experiment_path():
    session_id = os.getenv("SESSION_ID")
    if not session_id:
        raise EnvironmentError("SESSION_ID is not set. Please run the session ID setup first.")
    
    folder_name = f"ri_site_container_{session_id}-experiment"
    experiment_path = os.path.join(BASE_DIR, folder_name)
    
    if not os.path.exists(experiment_path):
        raise FileNotFoundError(f"Experiment directory does not exist: {experiment_path}")
    
    return experiment_path

def move_requirements(experiment_path):
    req_file = "requirements.txt"
    if os.path.isfile(req_file):
        dest = os.path.join(experiment_path, "data", "input", "workflow_input_files", req_file)
        shutil.move(req_file, dest)
        print(f"Moved {req_file} -> {dest}")

def copy_data_folder(experiment_path):
    src_data_dir = "data"
    dest_dir = os.path.join(experiment_path, "data", "input", "workflow_input_files")
    if os.path.isdir(src_data_dir):
        for item in os.listdir(src_data_dir):
            s = os.path.join(src_data_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"Copied contents of {src_data_dir} -> {dest_dir}")

def move_dockerfile(experiment_path):
    dockerfile = "Dockerfile"
    if os.path.isfile(dockerfile):
        dest = os.path.join(experiment_path, "environment", dockerfile)
        shutil.move(dockerfile, dest)
        print(f"Moved {dockerfile} -> {dest}")

def save_os_info(experiment_path):
    env_dir = os.path.join(experiment_path, "environment")
    os_info_file = os.path.join(env_dir, "os_info.txt")
    with open(os_info_file, "w") as f:
        f.write(f"System: {platform.system()}\n")
        f.write(f"Release: {platform.release()}\n")
        f.write(f"Version: {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Processor: {platform.processor()}\n")
    print(f"Saved OS info -> {os_info_file}")

def save_container_config(experiment_path):
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()

        pod_name = os.getenv("POD_NAME") or os.uname().nodename
        namespace = "jhub"
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        config_path = os.path.join(experiment_path, "environment", "pod_config.json")
        with open(config_path, "w") as f:
            json.dump(pod.to_dict(), f, indent=2)
        print(f"Saved Pod configuration -> {config_path}")
    except Exception as e:
        print(f"⚠️ Could not save Pod config: {e}")

def main():
    exp_path = get_experiment_path()
    move_requirements(exp_path)
    copy_data_folder(exp_path)
    move_dockerfile(exp_path)
    save_os_info(exp_path)
    save_container_config(exp_path)

if __name__ == "__main__":
    main()
