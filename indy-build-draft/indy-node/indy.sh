#!/bin/bash

. ./indy_env.sh

if [[ -n "${INDY_GENESIS_INIT}" ]]; then
    echo "Generating genesis tnx"
    ./create_genesis.py --node-names $(echo $INDY_NODE_NAME,$INDY_INITIAL_POOL_NAMES | sed 's/,$//') --node-ips $(echo $INDY_NODE_IP,$INDY_INITIAL_POOL_IPS | sed 's/,$//')  --node-seeds $(echo $INDY_NODE_SEED,$INDY_INITIAL_POOL_SEEDS | sed 's/,$//') | tee gen.log
elif [[ -n "${INDY_NODE_INIT}" ]]; then
    echo "Generating node keys"
    init_indy_node $INDY_NODE_NAME $INDY_NODE_IP $INDY_NODE_PORT $INDY_NODE_IP $INDY_CLENT_PORT $INDY_NODE_SEED
fi

start_indy_node $INDY_NODE_NAME $INDY_NODE_IP $INDY_NODE_PORT $INDY_NODE_IP $INDY_CLENT_PORT
