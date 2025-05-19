#!/bin/bash
sudo apt-get update
sudo apt-get install -y libhdf5-dev libnetcdf-dev

pip install -r /home/jovyan/egi-ice-net-example/requirements.txt