"""
Script to export per-session Scaphandre energy metrics for all active JupyterHub singleuser pods.
Detects pods in the "jhub" namespace with label "component=singleuser-server",
fetches the power consumption metric from Prometheus over each pod's lifetime,
and writes a CSV file per pod.

Requirements:
  pip install kubernetes prometheus_api_client pandas

Usage:
  export PROM_URL=http://<prometheus-host>:9090
  python export_scaphandre_metrics.py [--namespace jhub] [--output-dir ./metrics]
"""
import os
import secrets
import json
from datetime import datetime, timezone
from prometheus_api_client import PrometheusConnect
from kubernetes import client, config
import pandas as pd

def export_metrics():
    # Load in-cluster or local kubeconfig
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = f"./{timestamp}_metrics_export"
    
    namespace = "jhub"

    # Connect to Prometheus
    prom = PrometheusConnect(url=os.getenv("PROM_URL", "http://localhost:8000"), disable_ssl=True)
    v1 = client.CoreV1Api()

    # Generate unique experiment ID (8 hex chars)
    experiment_id = secrets.token_hex(4)  # 32-bit hex
    # Discover all scaph_ metrics
    all_metrics = prom.get_label_values(label_name="__name__")
    scaph_metrics = sorted(m for m in all_metrics if m.startswith("scaph_"))
    print(f"Detected Scaphandre metrics: {scaph_metrics}")

    # Discover singleuser pods
    pods = v1.list_namespaced_pod(namespace=namespace, label_selector="component=singleuser-server")
    start_time = datetime.now(timezone.utc)
    end_time = datetime.now(timezone.utc)

    for pod in pods.items:
        pod_name = pod.metadata.name
        start_ts = pod.metadata.creation_timestamp
        end_ts = pod.metadata.deletion_timestamp or datetime.now(timezone.utc)
        
        # Create a per-pod experiment folder including pod name
        folder_name = f"{experiment_id}_{pod_name}_jupyter-experiment"
        pod_dir = os.path.join(output_root, folder_name)
        os.makedirs(pod_dir, exist_ok=True)

        for metric in scaph_metrics:
            print(f"Exporting {metric} for pod {pod_name}")
            # Fetch the metric range over the session
            data = prom.get_metric_range_data(
                metric_name=metric,
                start_time=start_ts,
                end_time=end_ts,
                label_config={"pod": pod_name},
            )
            if not data:
                print(f"No data for {metric} on {pod_name}")
                continue
            # Assume single timeseries per metric/pod
            series = data[0]
            rows = [
                {
                    "timestamp": datetime.fromtimestamp(float(ts), tz=timezone.utc),
                    metric: float(val)
                }
                for ts, val in series.get('values', [])
            ]
            df = pd.DataFrame(rows)
            csv_path = os.path.join(pod_dir, f"{metric}.csv")
            df.to_csv(csv_path, index=False)
            print(f"  → Wrote {len(df)} rows to {csv_path}")

    # Generate RO-Crate metadata for entire experiment
    generate_rocrate(output_root, experiment_id, start_ts, end_ts, scaph_metrics, pods)

def generate_rocrate(output_root, experiment_id, start_time, end_time, metrics, pods):
    # Build list of part file paths
    has_parts = []
    for pod in pods.items:
        pod_name = pod.metadata.name
        folder_name = f"{experiment_id}_{pod_name}_jupyter-experiment"
        for metric in metrics:
            has_parts.append(f"{folder_name}/{metric}.csv")
    metadata = {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
                "about": {"@id": ""},
                "dateCreated": start_time.isoformat(),
                "datePublished": end_time.isoformat(),
                "hasPart": has_parts
            }
        ]
    }
    metadata_path = os.path.join(output_root, "ro-crate-metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"RO-Crate metadata generated at {metadata_path}")

if __name__ == "__main__":
    export_metrics()


