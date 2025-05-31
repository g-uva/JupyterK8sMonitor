kubectl create configmap track-notebook \
  --from-file=notebook_tracker_experimentid.py=/home/goncalo/jhub-helm-config/configmap-track-experiment-service/notebook_tracker_experimentid.py \
  -n jhub