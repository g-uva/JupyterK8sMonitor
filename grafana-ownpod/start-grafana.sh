# Allows Grafana embedding (e.g., in <iframe>).
sudo sed -i 's/^[;#]*\s*allow_embedding\s*=\s*false/allow_embedding = true/' /etc/grafana/grafana.ini
sudo /bin/systemctl start grafana-server