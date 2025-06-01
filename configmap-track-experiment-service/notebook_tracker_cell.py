import os
import json
import hashlib
import datetime
import requests
from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult

# =============== EXPERIMENT TRACKER ====================

class ExperimentTracker:
    def __init__(self):
        self.experiment_id = self._new_experiment_id()
        self.start_time = datetime.datetime.utcnow()
        self.executed_cells = 0
        self.failed_cells = 0
        self.logs = []
        self.log_dir = f"/home/jovyan/experiment_logs/{self.experiment_id}/output/logs"
        os.makedirs(self.log_dir, exist_ok=True)
        print(f"[Experiment Tracking] Started experiment {self.experiment_id}")

    def _new_experiment_id(self):
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"exp-{hashlib.sha256(ts.encode()).hexdigest()[:8]}-{ts}"

    def pre_run_cell(self, info):
        self.cell_start_time = datetime.datetime.utcnow()
        self.current_cell_code = info.raw_cell.strip()
        self.logs.append(f"[{self.cell_start_time}] Starting cell execution.")

    def post_run_cell(self, result: ExecutionResult):
        cell_end_time = datetime.datetime.utcnow()
        # Ensure pre-run attributes exist
        if not hasattr(self, "cell_start_time"):
            self.cell_start_time = self.start_time
            self.current_cell_code = "<unknown cell>"
            self.logs.append(f"[{cell_end_time}] WARNING: pre_run_cell hook may not have run.")
    
        duration = (cell_end_time - self.cell_start_time).total_seconds()
        self.executed_cells += 1
        cell_summary = (self.current_cell_code[:60] + '...') if len(self.current_cell_code) > 60 else self.current_cell_code
    
        if result.error_in_exec:
            self.failed_cells += 1
            error_msg = f"[{cell_end_time}] ERROR in cell ({cell_summary}): {repr(result.error_in_exec)}"
            self.logs.append(error_msg)
            print(error_msg)
        else:
            success_msg = f"[{cell_end_time}] SUCCESS in cell ({cell_summary}) [{duration:.2f}s]"
            self.logs.append(success_msg)
            print(success_msg)

    def end_experiment(self):
        end_time = datetime.datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "experiment_id": self.experiment_id,
            "start_time": str(self.start_time),
            "end_time": str(end_time),
            "duration_sec": duration,
            "cells_executed": self.executed_cells,
            "cells_failed": self.failed_cells
        }
        # Save summary JSON
        summary_path = f"/home/jovyan/experiment_logs/{self.experiment_id}/metadata.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        # Save logs
        log_path = os.path.join(self.log_dir, "log.txt")
        with open(log_path, "w") as f:
            f.write("\n".join(self.logs))
        print(f"[Experiment Tracking] Experiment {self.experiment_id} completed and logged.")

        # Fetch Prometheus metrics
        self.export_prometheus_metrics()

    def export_prometheus_metrics(self):
        prometheus_url = "https://mc-a4.lab.uvalight.net/prometheus-goncalo/metrics"
        try:
            resp = requests.get(prometheus_url, timeout=5)
            if resp.status_code == 200:
                lines = resp.text.splitlines()
                scaph_lines = [line for line in lines if line.startswith("scaph_")]
                metrics_path = f"/home/jovyan/experiment_logs/{self.experiment_id}/output/scaphandre_metrics.txt"
                os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
                with open(metrics_path, "w") as f:
                    f.write("\n".join(scaph_lines))
                print(f"[Experiment Tracking] Scaphandre metrics saved to {metrics_path}")
            else:
                print(f"[Experiment Tracking] Failed to fetch Prometheus metrics: HTTP {resp.status_code}")
        except Exception as e:
            print(f"[Experiment Tracking] Error fetching Prometheus metrics: {e}")

# =============== REGISTER HOOKS ====================

tracker = ExperimentTracker()
ip = get_ipython()
ip.events.register('pre_run_cell', tracker.pre_run_cell)
ip.events.register('post_run_cell', tracker.post_run_cell)
print("[Experiment Tracking] IPython hooks registered.")

# To end the experiment and export metrics, call:
# tracker.end_experiment()
