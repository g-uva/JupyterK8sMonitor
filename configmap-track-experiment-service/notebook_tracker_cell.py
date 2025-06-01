from IPython import get_ipython
import datetime, hashlib, os, json

tracking = {
    "experiment_id": f"exp-{hashlib.sha256(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S').encode()).hexdigest()[:8]}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
    "start_time": datetime.datetime.utcnow(),
    "executed": 0
}

log_dir = f"/home/jovyan/experiment_logs/{tracking['experiment_id']}"
os.makedirs(log_dir, exist_ok=True)
print(f"[Experiment Tracking] Started experiment {tracking['experiment_id']}")

def pre_run_cell(info):
    tracking['executed'] += 1
    print(f"[Experiment Tracking] Running cell {tracking['executed']}")

def post_run_cell(result):
    pass  # Optional: you could capture result.output here

def end_experiment():
    end_time = datetime.datetime.utcnow()
    with open(f"{log_dir}/metadata.json", "w") as f:
        json.dump({
            "experiment_id": tracking["experiment_id"],
            "start_time": str(tracking["start_time"]),
            "end_time": str(end_time),
            "duration": (end_time - tracking["start_time"]).total_seconds(),
            "cells_executed": tracking["executed"]
        }, f, indent=2)
    print(f"[Experiment Tracking] Experiment {tracking['experiment_id']} completed and logged.")

# Register IPython hooks
ip = get_ipython()
ip.events.register('pre_run_cell', pre_run_cell)
ip.events.register('post_run_cell', post_run_cell)

print("[Experiment Tracking] IPython hooks registered. Tracking is active.")

# Optionally: Call `end_experiment()` manually at the end of your session.
end_experiment()