#!/bin/bash

# Ensure that `--from-file` is correctly set in the folder structure to map to the script.
kubectl -n jhub create configmap export-metrics-script \
  --from-file=export_metrics.py=export_metrics/export_metrics.py
