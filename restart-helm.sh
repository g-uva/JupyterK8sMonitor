#!/bin/bash
kubectl delete pod/jupyter-goncalo -n jhub
helm upgrade jhub jupyterhub/jupyterhub --namespace jhub -f jhub-config-local.yaml --dry-run --debug
kubectl rollout restart deployment hub -n jhub