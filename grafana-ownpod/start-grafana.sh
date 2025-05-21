# Allows Grafana embedding (e.g., in <iframe>).
sudo sed -i 's/^[;#]*\s*allow_embedding\s*=\s*false/allow_embedding = true/' /etc/grafana/grafana.ini
grafana-server --homepath=/usr/share/grafana --config=/etc/grafana/grafana.ini &