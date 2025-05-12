###  `jhub-helm-config` repository
This is the repository that contains the configuration files for the Helm Zero to Jupyter Kubernetes cluster with Scaphandre.

This is a configuration for the server: https://mc-a4.lab.uvalight.net/.
> If you want to have access to the server (filesystem and others), please contact g.j.teixeiradepinhoferreira@uva.nl.

To install the repo, just run: `git clone git@github.com:g-uva/jhub-helm-config.git`.
- Repository on Github: https://github.com/g-uva/jhub-helm-config.

---

#### Infrastructure configuration
> The reference for the steps come from the official Zero to Jupyter documentation.
1. Install Helm.
2. Install Kubernetes and `kubectl`.
```sh
# If you're using SSH extension for VS code, make sure you have writing permissions:
ls -l ~/<your_file>
ls -ld ~ # Pointing to the /home/user/ root.

# As long as you have sudo access rights, you should set this as follows:
sudo chown -R $(whoami):$(whoami) ~ # Extending the automatic reading/writing access rights to the home folder.
```
3. Install all the repositories from Helm using the `yaml` files.
```sh
# -------------
# JupyterHub chart installation.
# -------------
helm install jhub jupyterhub/jupyterhub \
-n jhub --create-namespace \
--values ./jhub-config.yaml # Point to the configuration file for JupyterHub.

# -------------
# Monitoring (Prometheus + Grafana) chart installation.
# -------------
helm install monitoring prometheus-community/kube-prometheus-stack \
-n monitoring --create-namespace \
--values ./monitoring-config.yaml # Point to the configuration file for Monitoring.

# Update any repository (in case the YAML file is changed).
# Note: replace the namespace and repository accordingly.
helm upgrade --install jhub jupyterhub/jupyterhub -n jhub --values ./jhub-config.yaml
```

4. Apply PodMonitor and Nginx configurations.
5. The app should be ready to use! 👍

#### Metrics files (to be organised by @goncalo)
- Files to be run **outside** of the cluster (this should be done, not to worry about the Kubernetes-only user):
     - `pod-reader-rolebinding.yaml`: It allows Jupyter to read Kube and Pod configuration from within the Pod.
          - You must run `kubectl apply -f export-metrics-pod/pod-reader-rolebinding.yaml` during the configuration on the local server, outside of the Kubernetes cluster.
---

#### Run workflows and extract metrics (examples)
For the moment, the configuration files can be found in `/home/goncalo/jhub-helm-config/export-metrics-pod/`
- Download the script files from the [Google Drive folder](https://drive.google.com/drive/folders/1NuyVLMKWd6GW7lNOmeb9H2g25PlrpqXT?usp=drive_link).

Notebook and package files:
- `analysis.ipynb`: example notebook file provided by Shashikant.
- `requirements.txt`: list of packages to be installed by Python (for now it is manual).
    - Run `pip install -r requirements.txt` to install the packages needed to run the notebook.

List of files and actions:
- `export_metrics_ownpod.py`: copy it to the `root` (typically `/home/jovyan`).
- `export-metrics.sh`: copy it to the `root` + execute `chmod +x ./export-metrics.sh` in order to make it executable.

##### Example notebooks tutorial
> For the moment, some example notebooks can be used to simulate the workflow.

> The example notebooks' data can be downloaded from the following links:
- [Workflow 1](https://github.com/shashikantilager/data-center-characterization) *(Just for reference, please read the instructions to put the data into the `/data/...` folder).*
    1. [Notebook from Shashikant](https://drive.google.com/file/d/1FUi9xw3Y0VuzUhbqicEM2HnDONcNtgwB/view?usp=drive_link)
    2. [Dataset 01](https://drive.google.com/file/d/1cW7jggF2-TmPBrQEpJDtx0vOYs5Me8Cg/view?usp=drive_link)
    3. [Dataset 02](https://drive.google.com/file/d/1svqM1wrkxtCk9nZ90aJEvXGlBnNr8kRN/view?usp=drive_link) 
- [Workflow 2](https://github.com/atlarge-research/2024-icpads-hpc-workload-characterization)
- Enol's notebook (not done yet).

```sh
export-metrics/
└── 1a2b3c4d_jupyter-goncalo_jupyter-experiment/
    ├── scaph_host_energy_microwatts.csv
    ├── scaph_process_power_consumption.csv
    └── ... other scaph_*.csv files
ro-crate-metadata.json
```

##### Exiting the notebook
For the moment, in order to "kill" the pod, the server must be stopped. To do that you must go to `File > Hub Control Panel` and click the button `Stop my server`