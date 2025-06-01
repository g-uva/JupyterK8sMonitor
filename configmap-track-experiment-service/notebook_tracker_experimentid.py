from jupyter_server.serverapp import ServerApp as NotebookApp
from jupyter_server.services.kernels.kernelmanager import MappingKernelManager
import datetime, hashlib, os, json

class ExperimentTrackingKernelManager(MappingKernelManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracking = {}  # Per-kernel tracking

    def _get_kernel_id(self, session):
        for kid, k in self._kernels.items():
            if k.session.session == session:
                return kid
        return None

    async def execute_request(self, stream, ident, parent):
        kernel_id = self._get_kernel_id(stream.session)
        if kernel_id not in self.tracking:
            self.tracking[kernel_id] = {
                "experiment_id": self._new_experiment_id(),
                "start_time": datetime.datetime.utcnow(),
                "pending": 0,
                "executed": 0
            }
            print(f"[Experiment Tracking] Started experiment {self.tracking[kernel_id]['experiment_id']}")

        self.tracking[kernel_id]["pending"] += 1

        reply = await super().execute_request(stream, ident, parent)
        self.tracking[kernel_id]["executed"] += 1
        self.tracking[kernel_id]["pending"] -= 1

        # Check if all cells done
        if self.tracking[kernel_id]["pending"] == 0:
            self._end_experiment(kernel_id)

        return reply

    def _new_experiment_id(self):
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"exp-{hashlib.sha256(ts.encode()).hexdigest()[:8]}-{ts}"

    def _end_experiment(self, kernel_id):
        info = self.tracking[kernel_id]
        end_time = datetime.datetime.utcnow()
        log_dir = f"/home/jovyan/experiment_logs/{info['experiment_id']}"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/metadata.json", "w") as f:
            json.dump({
                "experiment_id": info["experiment_id"],
                "start_time": str(info["start_time"]),
                "end_time": str(end_time),
                "duration": (end_time - info["start_time"]).total_seconds(),
                "cells_executed": info["executed"]
            }, f, indent=2)
        print(f"[Experiment Tracking] Experiment {info['experiment_id']} completed and logged.")
        del self.tracking[kernel_id]
    
    print("[Experiment Tracking] Tracker module loaded successfully.")
    
print("[Experiment Tracking] Applying custom KernelManager.")
NotebookApp.kernel_manager_class = ExperimentTrackingKernelManager
