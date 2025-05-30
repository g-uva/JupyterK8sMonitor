kubectl create configmap starter-notebook \
  --from-file=GD_EcoJupyter_Tutorial.ipynb=/home/goncalo/jhub-helm-config/tutorial-notebook/GD_EcoJupyter_Tutorial.ipynb \
  -n jhub

kubectl create configmap stress-notebook \
  --from-file=GD_EcoJupyter_StressTest.ipynb=/home/goncalo/jhub-helm-config/tutorial-notebook/GD_EcoJupyter_StressTest.ipynb \
  -n jhub

