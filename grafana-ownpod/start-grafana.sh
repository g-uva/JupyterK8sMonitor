#!/bin/bash

CONFIG_FILE="/etc/grafana/grafana.ini"
DOMAIN="mc-a4.lab.uvalight.net"
ROOT_PATH="/grafana"

# Backup
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
if [ $? -ne 0 ]; then
    echo "❌ Failed to backup $CONFIG_FILE"
    exit 1
fi

# Patch the config
sudo sed -i \
    -e '/^\[server\]/,/^\[/{s/^[;#]*\s*root_url\s*=.*/root_url = https:\/\/'"$DOMAIN$ROOT_PATH"'/}' \
    -e '/^\[server\]/,/^\[/{s/^[;#]*\s*serve_from_sub_path\s*=.*/serve_from_sub_path = true/}' \
    -e '/^\[server\]/,/^\[/{s/^[;#]*\s*enforce_domain\s*=.*/enforce_domain = false/}' \
    -e '/^\[security\]/,/^\[/{s/^[;#]*\s*allow_embedding\s*=.*/allow_embedding = true/}' \
    -e '/^\[security\]/,/^\[/{s/^[;#]*\s*cookie_secure\s*=.*/cookie_secure = true/}' \
    -e '/^\[security\]/,/^\[/{s/^[;#]*\s*cookie_samesite\s*=.*/cookie_samesite = none/}' \
    "$CONFIG_FILE"

echo "✅ Config patched: $CONFIG_FILE"

# Restart Grafana (cleanly kill any background process)
sudo ./restart-grafana.sh
echo "✅ Grafana restarted and running at https://$DOMAIN$ROOT_PATH"
