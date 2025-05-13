import argparse
import os

csv_dir_name = "csv"

def generate_rocrate(base_dir, pod_name, metrics, start_time, end_time):
    has_parts = [f"{csv_dir_name}/{pod_name}/{m}.csv" for m in metrics]
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
    print(f"All done! Files under {main_dir}")
    
if __name__ == "__main__":
     parser = argparse.ArgumentParser()
     parser.add_argument("--pod-name", required=True, help="Name of the pod to export metrics from")
     parser.add_argument("--start-time", required=True, help="Start time for the metrics in ISO format")
     parser.add_argument("--end-time", required=True, help="End time for the metrics in ISO format")
     parser.add_argument("--output-root", default="/tmp", help="Root directory for output files")
     args = parser.parse_args()
     
     pod_name = args.pod_name
     start_time = datetime.fromisoformat(args.start_time)
     end_time = datetime.fromisoformat(args.end_time)
     output_root = args.output_root
     
     generate_metrics(pod_name, start_time, end_time, output_root)