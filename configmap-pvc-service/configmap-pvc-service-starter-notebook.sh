kubectl create configmap starter-notebook \
  --from-file=GD_EcoJupyter_Tutorial.ipynb=/home/goncalo/jhub-helm-config/tutorial-notebook/GD_EcoJupyter_Tutorial.ipynb \
  -n jhub
