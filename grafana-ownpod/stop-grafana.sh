# Kill existing Grafana process cleanly
PID=$(sudo lsof -ti :3000)
if [ -n "$PID" ]; then
    echo "🔪 Killing Grafana process on port 3000 (PID: $PID)"
    sudo kill "$PID"
    sleep 1
else
    echo "ℹ️ No existing Grafana process on port 3000"
fi