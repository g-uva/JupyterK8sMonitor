kubectl delete configmap track-notebook -n jhub
kubectl create configmap track-notebook \
  --from-file=notebook_tracker_experimentid.py=/home/goncalo/jhub-helm-config/configmap-track-experiment-service/notebook_tracker_experimentid.py \
  -n jhub
helm upgrade jhub jupyterhub/jupyterhub -n jhub -f jhub-config-local.yaml
kubectl delete pod jupyter-goncalo -n jhub