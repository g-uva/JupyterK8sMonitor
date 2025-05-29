# kubectl create configmap shashikant-notebook-example \
#   --from-file="/home/goncalo/jhub-helm-config/shashikant-notebook/" \
#   -n jhub

kubectl apply -f /home/jovyan/configmap-pvc-service/pvc-loader.yaml
cp /home/goncalo/shashikant-notebook /jhub/pvc-loader:/mnt/shashikant-notebook
kubectl delete pod pvc-loader -n jhub
