sudo systemctl stop grafana-server || true
sudo bash ./stop-grafana.sh || true
sudo apt-get purge -y grafana
sudo apt-get autoremove -y
sudo rm -rf /etc/grafana /var/lib/grafana /usr/share/grafana /var/log/grafana
