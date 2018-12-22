#!/bin/bash

if [[ -z "${INDY_NETWORK_NAME}" ]]; then 
    export INDY_NETWORK_NAME=MESH
fi

if [[ -z "${INDY_NODE_INFO_DIR}" ]]; then 
    export INDY_NODE_INFO_DIR=/var/lib/indy/node
fi

if [[ -z "${INDY_NODE_KEYS_DIR}" ]]; then 
    export INDY_NODE_KEYS_DIR=/var/lib/indy/keys
fi

if [[ -z "${INDY_NODE_GENESIS_DIR}" ]]; then 
    export INDY_NODE_GENESIS_DIR=/var/lib/indy/genesis
fi

if [[ -z "${INDY_NODE_IP}" ]]; then 
    export INDY_NODE_IP=$(hostname -i)
fi

if [[ -z "${INDY_NODE_PORT}" ]]; then 
    export INDY_NODE_PORT=9701
fi

if [[ -z "${INDY_CLENT_PORT}" ]]; then 
    export INDY_CLENT_PORT=9702
fi

mkdir -p $INDY_NODE_GENESIS_DIR/$INDY_NETWORK_NAME
mkdir -p $INDY_NODE_INFO_DIR/$INDY_NETWORK_NAME
mkdir -p $INDY_NODE_KEYS_DIR/$INDY_NETWORK_NAME/keys

LS=$(ls -1 $INDY_NODE_KEYS_DIR/$INDY_NETWORK_NAME/keys) 
if [[ $(echo "$LS"|wc -l) -eq 2 ]] && [[ $(echo "$LS"|grep 'C'|wc -l) -eq 1 ]]; then
    export INDY_NODE_NAME=$(echo "$LS"|head -1|sed 's/C$//')
else
    export INDY_NODE_INIT=true

    if [[ -z "${INDY_NODE_SEED}" ]]; then 
        export INDY_NODE_SEED=$(pwgen -s 32 1)
    fi
fi

if [[ -z "${INDY_NODE_NAME}" ]]; then 
    export INDY_NODE_NAME=$(petname -w 4)
fi

if [[ -n "${INDY_GENESIS_NODE}" ]]; then 
	nw_dir="$INDY_NODE_GENESIS_DIR/$INDY_NETWORK_NAME"
	if [ ! -f "$nw_dir/domain_transactions_genesis" ] || [ ! -f "$nw_dir/pool_transactions_genesis" ]
	then
		export INDY_GENESIS_INIT=true
	fi
fi 

