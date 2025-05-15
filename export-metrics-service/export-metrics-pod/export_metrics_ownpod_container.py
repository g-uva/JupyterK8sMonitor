"""
Export Scaphandre energy metrics for *this* pod only, without any kube-config.
Fetches all scaph_* metrics from Prometheus over a user-specified window
(or the last 24 h by default), writes one CSV per metric, and generates RO-Crate JSON.

Requires:
    pip install prometheus_api_client pandas

Usage:
    export PROM_URL=http://<prom-host>:9090
    python export_metrics.py
"""

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


def export_metrics(pod_name: str, start_time: datetime, end_time: datetime, output_root: str):
    prom = PrometheusConnect(
        "http://localhost:9090",
        disable_ssl=True
    )

    # Discover scaph_ metrics
    all_metrics = prom.get_label_values(label_name="__name__")
    scaph_metrics = sorted(m for m in all_metrics if m.startswith("scaph_"))
    print(f"Detected Scaphandre metrics: {scaph_metrics}")

    # Prepare output directories
    random_hex = os.urandom(6).hex()
    now = datetime.now()
    ts = int(now.timestamp())
    os.makedirs(output_root, exist_ok=True)
    main_dir = os.path.join(output_root, f"{random_hex}-{ts}-{pod_name}-metrics-export")
    metrics_dir = os.path.join(main_dir, csv_dir_name)
    os.makedirs(metrics_dir, exist_ok=True)

    # Pull and dump each metric
    for metric in scaph_metrics:
        print(f" → Exporting {metric} for pod {pod_name}")
        data = prom.get_metric_range_data(
            metric_name=metric,
            start_time=start_time,
            end_time=end_time,
        )
        if not data:
            print(f"    • no data for {metric}")
            continue

        # Build DataFrame
        rows = [
            {
                "timestamp": datetime.fromtimestamp(float(ts), tz=timezone.utc),
                metric: float(val)
            }
            for ts, val in data[0].get("values", [])
        ]
        df = pd.DataFrame(rows)


        csv_path = os.path.join(metrics_dir, f"{metric}.csv")
        df.to_csv(csv_path, index=False)
        print(f"    • wrote {len(df)} rows to {csv_path}")

    # Generating RO-Crate metadata
    generate_rocrate(main_dir, scaph_metrics, start_time, end_time)
    print(f"All done! Files under {main_dir}")


def generate_rocrate(base_dir, metrics, start_time, end_time):
    has_parts = [f"{csv_dir_name}/{m}.csv" for m in metrics]
    metadata = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [{
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
            "about": {"@id": ""},
            "dateCreated": start_time.isoformat(),
            "datePublished": end_time.isoformat(),
            "hasPart": has_parts
        }]
    }
    path = os.path.join(base_dir, "ro-crate-metadata.json")
    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"RO-Crate metadata at {path}")


if __name__ == "__main__":
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    p = argparse.ArgumentParser()

    args = p.parse_args()

    pod_name = os.getenv("POD_NAME") or os.uname().nodename
    
    pod = v1.read_namespaced_pod(name=pod_name, namespace="jhub")
    start = pod.status.start_time
    end = datetime.now(timezone.utc)
    
    output_dir = "/home/jovyan/export-metrics"
    os.makedirs(output_dir, exist_ok=True)

    export_metrics(pod_name, start, end, output_dir)
