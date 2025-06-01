from notebook.notebookapp import NotebookApp
from notebook.services.kernels.kernelmanager import MappingKernelManager
from jupyter_client import KernelManager
import datetime
import hashlib
import os
import json
import threading

class CustomKernelManager(MappingKernelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_sessions = {}  # Track experiment sessions per kernel

    def generate_experiment_id(self):
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_digest = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        return f"exp-{hash_digest}-{timestamp}"

    def record_experiment(self, kernel_id, metadata):
        log_dir = "/home/jovyan/experiment_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, f"experiment_{metadata['experiment_id']}.json")
        with open(log_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"[Experiment Tracking] Metadata saved at {log_path}")

    def start_kernel(self, *args, **kwargs):
        kernel_id = super().start_kernel(*args, **kwargs)
        self.execution_sessions[kernel_id] = {
            "experiment_id": None,
            "start_time": None,
            "execution_count": 0,
            "timer": None
        }
        return kernel_id

    def shutdown_kernel(self, kernel_id, *args, **kwargs):
        session = self.execution_sessions.get(kernel_id)
        if session and session["experiment_id"]:
            end_time = datetime.datetime.utcnow()
            duration = (end_time - session["start_time"]).total_seconds()
            metadata = {
                "experiment_id": session["experiment_id"],
                "kernel_id": kernel_id,
                "start_time": str(session["start_time"]),
                "end_time": str(end_time),
                "duration_sec": duration,
                "execution_count": session["execution_count"]
            }
            self.record_experiment(kernel_id, metadata)
        return super().shutdown_kernel(kernel_id, *args, **kwargs)

    async def execute_request(self, stream, ident, parent):
        kernel_id = self._kernel_id(stream.session)
        session = self.execution_sessions[kernel_id]

        if session["experiment_id"] is None:
            # Start a new experiment
            session["experiment_id"] = self.generate_experiment_id()
            session["start_time"] = datetime.datetime.utcnow()
            print(f"[Experiment Tracking] Run All Detected! Experiment ID: {session['experiment_id']}")

        session["execution_count"] += 1

        # Reset inactivity timer
        if session["timer"]:
            session["timer"].cancel()

        def end_experiment():
            end_time = datetime.datetime.utcnow()
            duration = (end_time - session["start_time"]).total_seconds()
            metadata = {
                "experiment_id": session["experiment_id"],
                "kernel_id": kernel_id,
                "start_time": str(session["start_time"]),
                "end_time": str(end_time),
                "duration_sec": duration,
                "execution_count": session["execution_count"]
            }
            self.record_experiment(kernel_id, metadata)
            session["experiment_id"] = None
            session["execution_count"] = 0
            session["start_time"] = None

        # End experiment after 10 sec of inactivity
        session["timer"] = threading.Timer(10, end_experiment)
        session["timer"].start()

        # Call parent execute_request
        return await super().execute_request(stream, ident, parent)

    def _kernel_id(self, session):
        for kernel_id, kernel_session in self._kernels.items():
            if kernel_session.session.session == session:
                return kernel_id
        return None

NotebookApp.kernel_manager_class = CustomKernelManager
