#!/bin/bash

# Cargar la configuración desde el archivo YAML
CONFIG_FILE="./config/peerSlave_config.yaml"

ip=$(cat $CONFIG_FILE | grep 'ip:' | awk '{print $2}')
port=$(cat $CONFIG_FILE | grep 'port:' | awk '{print $2}')
ip_seed=$(cat $CONFIG_FILE | grep 'ip_seed:' | awk '{print $2}')
port_seed=$(cat $CONFIG_FILE | grep 'port_seed:' | awk '{print $2}')

# Ejecutar el script Python con los valores de la configuración

echo "IP: $ip_seed"

exec python ./run_node_api.py "$ip" "$port" "$ip_seed" "$port_seed"
