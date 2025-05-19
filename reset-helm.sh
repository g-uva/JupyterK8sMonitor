helm uninstall jhub -n jhub
kubectl delete pvc --all -n jhub
helm install jhub jupyterhub/jupyterhub -n jhub -f jhub-config-local.yaml
kubectl -n jhub patch svc proxy-public \
  --type='merge' \
  -p '{"spec":{"externalIPs":["192.168.49.2"]}}'