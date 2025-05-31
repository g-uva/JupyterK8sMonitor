from notebook.notebookapp import NotebookApp
from notebook.services.kernels.kernelmanager import MappingKernelManager
import datetime
import hashlib
import os
import json

class CustomKernelManager(MappingKernelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kernel_start_times = {}
        self.experiment_ids = {}

    def generate_experiment_id(self):
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_digest = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        return f"exp-{hash_digest}-{timestamp}"

    def start_kernel(self, *args, **kwargs):
        kernel_id = super().start_kernel(*args, **kwargs)
        start_time = datetime.datetime.utcnow()
        experiment_id = self.generate_experiment_id()

        # Ensure experiment log directory exists at kernel start
        log_dir = "/home/jovyan/experiment_logs"
        os.makedirs(log_dir, exist_ok=True)

        self.kernel_start_times[kernel_id] = start_time
        self.experiment_ids[kernel_id] = experiment_id

        print(f"[Experiment Tracking] Kernel {kernel_id} started at {start_time}. Experiment ID: {experiment_id}")
        return kernel_id

    def shutdown_kernel(self, kernel_id, *args, **kwargs):
        end_time = datetime.datetime.utcnow()
        start_time = self.kernel_start_times.get(kernel_id)
        experiment_id = self.experiment_ids.get(kernel_id)
        duration = (end_time - start_time).total_seconds() if start_time else None

        metadata = {
            "experiment_id": experiment_id,
            "kernel_id": kernel_id,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "duration_sec": duration
        }

        log_dir = "/home/jovyan/experiment_logs"
        os.makedirs(log_dir, exist_ok=True)  # Optional safeguard here too
        log_path = os.path.join(log_dir, f"experiment_{experiment_id}.json")

        with open(log_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"[Experiment Tracking] Kernel {kernel_id} stopped. Metadata saved at {log_path}.")
        return super().shutdown_kernel(kernel_id, *args, **kwargs)

NotebookApp.kernel_manager_class = CustomKernelManager
