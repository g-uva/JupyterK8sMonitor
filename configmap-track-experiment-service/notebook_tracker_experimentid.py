import datetime
import hashlib
import os
import json
from IPython import get_ipython

class ExperimentTracker:
    def __init__(self):
        self.experiment_id = self._new_experiment_id()
        self.start_time = datetime.datetime.utcnow()
        self.executed_cells = 0
        self.log_dir = f"/home/jovyan/experiment_logs/{self.experiment_id}"
        os.makedirs(self.log_dir, exist_ok=True)
        print(f"[Experiment Tracking] Started experiment {self.experiment_id}")

    def _new_experiment_id(self):
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"exp-{hashlib.sha256(ts.encode()).hexdigest()[:8]}-{ts}"

    def log_start(self):
        print(f"[Experiment Tracking] Cell execution started.")

    def log_end(self):
        self.executed_cells += 1
        print(f"[Experiment Tracking] Cell execution completed. Total so far: {self.executed_cells}")
        # Optional: Save incremental progress
        with open(f"{self.log_dir}/progress.json", "w") as f:
            json.dump({"cells_executed": self.executed_cells}, f, indent=2)

    def finalize(self):
        end_time = datetime.datetime.utcnow()
        metadata = {
            "experiment_id": self.experiment_id,
            "start_time": str(self.start_time),
            "end_time": str(end_time),
            "duration": (end_time - self.start_time).total_seconds(),
            "cells_executed": self.executed_cells
        }
        with open(f"{self.log_dir}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"[Experiment Tracking] Experiment {self.experiment_id} completed and logged.")

# Register hooks with IPython
ip = get_ipython()
if ip:
    tracker = ExperimentTracker()
    ip.events.register('pre_execute', tracker.log_start)
    ip.events.register('post_execute', tracker.log_end)
    import atexit
    atexit.register(tracker.finalize)
    print("[Experiment Tracking] IPython hooks registered.")
else:
    print("[Experiment Tracking] Not running inside an IPython environment.")
