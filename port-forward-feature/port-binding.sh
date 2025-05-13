kubectl -n jhub patch svc proxy-public \
  --type='merge' \
  -p '{"spec":{"externalIPs":["192.168.49.2"]}}'