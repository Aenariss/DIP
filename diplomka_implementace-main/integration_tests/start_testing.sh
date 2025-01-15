#!/bin/bash

client_config="./example_configs/client.json"
server_config="./example_configs/server.json"

nohup python3 fingerprinting_server/run.py > server.log 2>&1 &  

cd client_simulator

python3 start.py "$client_config" "$server_config"

integration_testing=$(jq -r '.integration_testing' "$client_config")

if [ "$integration_testing" = "true" ]; then
    cd ../test_data
    unbuffer python3 start.py | tee >(sed "s,\x1B\[[0-9;]*[a-zA-Z],,g" > ./outputs/$(date +'%Y%m%d%H%M%S').log)
fi