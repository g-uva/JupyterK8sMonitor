# First updates
sudo apt-get update
sudo apt-get install -y pkg-config libssl-dev

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
rustup install 1.65.0
rustup override set 1.65.0

# Install Scaphandre
git clone https://github.com/hubblo-org/scaphandre.git
cd scaphandre
cargo build --release

# Install Prometheus
cd ~
wget https://github.com/prometheus/prometheus/releases/download/v2.52.0/prometheus-2.52.0.linux-amd64.tar.gz
tar xzf prometheus-2.52.0.linux-amd64.tar.gz
cd prometheus-2.52.0.linux-amd64

# Start Prometheus server
PROMETHEUS_CONFIG=$(cat <<EOF
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'scaphandre-local'
    static_configs:
      - targets: ['localhost:8081']
EOF
)
echo "$PROMETHEUS_CONFIG" > prometheus.yml
./prometheus --config.file=prometheus.yml --web.listen-address=0.0.0.0:9090