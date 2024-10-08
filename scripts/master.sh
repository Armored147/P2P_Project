#!/bin/bash

# Cargar la configuración desde el archivo YAML
CONFIG_FILE="./config/peerMaster_config.yaml"

ip=$(cat $CONFIG_FILE | grep 'ip:' | awk '{print $2}')
port=$(cat $CONFIG_FILE | grep 'port:' | awk '{print $2}')

# Ejecutar el script Python con los valores de la configuración
exec python ./run_node_api.py "$ip" "$port" 
