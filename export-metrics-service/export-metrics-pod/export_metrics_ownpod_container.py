import os
import json
from datetime import datetime, timezone
import argparse
from kubernetes import client, config
import pandas as pd
from prometheus_api_client import PrometheusConnect

csv_dir_name = "csv"

def parse_time(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def export_metrics(pod_name: str, start_time: datetime, end_time: datetime, output_root: str, session_id: str):
    prom = PrometheusConnect(
        "http://localhost:9090",
        disable_ssl=True
    )

    all_metrics = prom.get_label_values(label_name="__name__")
    scaph_metrics = sorted(m for m in all_metrics if m.startswith("scaph_"))
    print(f"Detected Scaphandre metrics: {scaph_metrics}")

    # Prepare output directories
    now = datetime.now()
    ts = int(now.timestamp())
    os.makedirs(output_root, exist_ok=True)
    # main_dir = os.path.join(output_root, f"{session_id}-{ts}-{pod_name}-metrics-export")
    # metrics_dir = os.path.join(main_dir, csv_dir_name)
    # os.makedirs(metrics_dir, exist_ok=True)

    all_data = {}

    for metric in scaph_metrics:
        print(f" → Exporting {metric} for pod {pod_name}")
        data = prom.get_metric_range_data(
            metric_name=metric,
            start_time=start_time,
            end_time=end_time,
        )
        if not data or "values" not in data[0]:
            print(f"    • no data for {metric}")
            continue

        for ts, val in data[0]["values"]:
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            if dt not in all_data:
                all_data[dt] = {}
            all_data[dt][metric] = float(val)

    # Build a DataFrame from combined data
    all_rows = [{"timestamp": dt, **metrics} for dt, metrics in sorted(all_data.items())]
    df_all = pd.DataFrame(all_rows).sort_values("timestamp")
    csv_path = os.path.join(output_root, "scaph_metrics_combined.csv")
    df_all.to_csv(csv_path, index=False)
    print(f"    • wrote {len(df_all)} rows to {csv_path}")

    # generate_rocrate(main_dir, start_time, end_time)
    print(f"All done! Files under {main_dir}")

# def generate_rocrate(base_dir, start_time, end_time):
#     has_parts = []
#     for root, _, files in os.walk(base_dir):
#         for f in files:
#             if f.endswith(".csv"):
#                 rel_path = os.path.relpath(os.path.join(root, f), start=base_dir)
#                 has_parts.append(rel_path.replace("\\", "/"))  # for Windows compatibility

#     metadata = {
#         "@context": "https://w3id.org/ro/crate/1.1/context",
#         "@graph": [{
#             "@id": "ro-crate-metadata.json",
#             "@type": "CreativeWork",
#             "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
#             "about": {"@id": ""},
#             "dateCreated": start_time.isoformat(),
#             "datePublished": end_time.isoformat(),
#             "hasPart": has_parts
#         }]
#     }

#     path = os.path.join(base_dir, "ro-crate-metadata.json")
#     with open(path, "w") as f:
#         json.dump(metadata, f, indent=2)
#     print(f"RO-Crate metadata at {path}")

if __name__ == "__main__":
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    p = argparse.ArgumentParser()
    args = p.parse_args()

    pod_name = os.getenv("POD_NAME") or os.uname().nodename
    pod = v1.read_namespaced_pod(name=pod_name, namespace="jhub")
    start = pod.status.start_time
    end = datetime.now(timezone.utc)

    session_id = os.getenv("SESSION_ID")
    output_dir = f"/home/jovyan/ri_site_container_{session_id}-experiment"
    os.makedirs(output_dir, exist_ok=True)

    export_metrics(pod_name, start, end, output_dir, session_id)
    