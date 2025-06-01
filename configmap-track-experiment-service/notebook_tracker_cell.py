import os
import json
import hashlib
import pandas as pd
from datetime import datetime, timezone
import requests
from IPython import get_ipython
from IPython.core.interactiveshell import ExecutionResult
from prometheus_api_client import PrometheusConnect

class ExperimentTracker:
    def __init__(self):
        self.experiment_id = self._new_experiment_id()
        self.start_time = datetime.utcnow()
        self.executed_cells = 0
        self.failed_cells = 0
        self.logs = []
        self.log_dir = f"/home/jovyan/experiment_logs/{self.experiment_id}/output/logs"
        self.metrics_dir = f"/home/jovyan/experiment_logs/{self.experiment_id}/output/metrics"
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.metrics_dir, exist_ok=True)
        print(f"[Experiment Tracking] Started experiment {self.experiment_id}")

    def export_scaph_metrics(self, start_time, end_time):
        prom_url = "https://mc-a4.lab.uvalight.net/prometheus-goncalo/"
        prom = PrometheusConnect(url=prom_url, disable_ssl=True)
        try:
            all_metrics = prom.get_label_values(label_name="__name__")
            scaph_metrics = sorted([m for m in all_metrics if m.startswith("scaph_")])
            print(f"[Experiment Tracking] Detected Scaphandre metrics: {scaph_metrics}")
        except Exception as e:
            print(f"[Experiment Tracking] Failed to fetch Prometheus metrics: {e}")
            return

        all_data = {}
        for metric in scaph_metrics:
            print(f"[Experiment Tracking] Exporting {metric}")
            try:
                data = prom.get_metric_range_data(metric_name=metric, start_time=start_time, end_time=end_time)
                if not data or "values" not in data[0]:
                    print(f"[Experiment Tracking] No data for {metric}")
                    continue
                for ts, val in data[0]["values"]:
                    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                    if dt not in all_data:
                        all_data[dt] = {}
                    all_data[dt][metric] = float(val)
            except Exception as e:
                print(f"[Experiment Tracking] Error fetching data for {metric}: {e}")

        if not all_data:
            print(f"[Experiment Tracking] No Scaphandre metrics collected.")
            return

        rows = [{"timestamp": dt, **metrics} for dt, metrics in sorted(all_data.items())]
        df = pd.DataFrame(rows).sort_values("timestamp")
        csv_path = os.path.join(self.metrics_dir, "scaph_metrics_combined.csv")
        df.to_csv(csv_path, index=False)
        print(f"[Experiment Tracking] Wrote {len(df)} rows to {csv_path}")

    def _new_experiment_id(self):
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"exp-{hashlib.sha256(ts.encode()).hexdigest()[:8]}-{ts}"

    def pre_run_cell(self, info):
        self.cell_start_time = datetime.utcnow()
        self.current_cell_code = info.raw_cell.strip()
        self.logs.append(f"[{self.cell_start_time}] Starting cell execution.")

    def post_run_cell(self, result: ExecutionResult):
        cell_end_time = datetime.utcnow()
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
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        summary = {
            "experiment_id": self.experiment_id,
            "start_time": str(self.start_time),
            "end_time": str(end_time),
            "duration_sec": duration,
            "cells_executed": self.executed_cells,
            "cells_failed": self.failed_cells
        }
        summary_path = f"/home/jovyan/experiment_logs/{self.experiment_id}/metadata.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        log_path = os.path.join(self.log_dir, "log.txt")
        with open(log_path, "w") as f:
            f.write("\n".join(self.logs))
        print(f"[Experiment Tracking] Experiment {self.experiment_id} completed and logged.")
        self.export_scaph_metrics(self.start_time, end_time)

# Register hooks.
tracker = ExperimentTracker()
ip = get_ipython()
ip.events.register('pre_run_cell', tracker.pre_run_cell)
ip.events.register('post_run_cell', tracker.post_run_cell)
print("[Experiment Tracking] IPython hooks registered.")