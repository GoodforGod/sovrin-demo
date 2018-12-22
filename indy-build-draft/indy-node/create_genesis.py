#! /usr/bin/env python3

from plenum.common.test_network_setup import TestNetworkSetup
from plenum.common.config_helper import PConfigHelper, PNodeConfigHelper
from plenum.common.member.member import Member
from plenum.common.member.steward import Steward
from plenum.common.constants import STEWARD, TRUSTEE
from plenum.common.signer_did import DidSigner
from plenum.common.keygen_utils import initNodeKeysForBothStacks
from plenum.common.util import hexToFriendly

from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper, NodeConfigHelper
from indy_common.txn_util import getTxnOrderedFields

from stp_core.crypto.nacl_wrappers import Signer
from stp_core.common.util import adict

import os
import logging
import argparse
import string
import random

def generateSeed():
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits    
    return ''.join(random.choice(alphabet) for _ in range(32))

if __name__ == "__main__":
    logger = logging.getLogger()
    config = getConfig()
    txFieldOrder = getTxnOrderedFields()

    logging.FileHandler('/var/lib/indy.log')

    parser = argparse.ArgumentParser(description="Generate pool transactions")
    parser.add_argument('--node-names', 
                        required=True)
    parser.add_argument('--node-ips', 
                        required=True)
    parser.add_argument('--node-seeds', 
                        required=True)                    
    parser.add_argument('--node-port', 
                        default=9701)       
    parser.add_argument('--client-port', 
                        default=9702)
    parser.add_argument('--append', 
                        default=False)
                              
    args = parser.parse_args()

    nodeIpsString = args.node_ips
    nodeSeedsString = args.node_seeds
    nodeNamesString = args.node_names
    nodeIps = nodeIpsString.split(',')
    nodeSeeds = nodeSeedsString.split(',')
    nodeNames = nodeNamesString.split(',')

    assert len(nodeIps) == len(nodeSeeds) and len(nodeIps) == len(nodeNames)

    nodeCountToInit = len(nodeIps)

    config_helper_class=PConfigHelper
    config_helper = config_helper_class(config, chroot=None)
    genesis_dir = config_helper.genesis_dir + "/" + config.NETWORK_NAME
    os.makedirs(genesis_dir, exist_ok=True)
    keys_dir = config_helper.keys_dir + "/" + config.NETWORK_NAME + "/keys"
    os.makedirs(keys_dir, exist_ok=True)

    poolLedger = TestNetworkSetup.init_pool_ledger(args.append, genesis_dir, config)
    domainLedger = TestNetworkSetup.init_domain_ledger(args.append, genesis_dir, config, txFieldOrder)

    genesis_protocol_version = 2

    trustee_seed = generateSeed()
    logger.info('Trustee seed will be %s', trustee_seed)
    trustee_seed = trustee_seed.encode()    
    trustee_signer = DidSigner(seed=trustee_seed)
    trustee_def = adict()
    trustee_def.name = nodeNames[0] + "-trustee"
    trustee_def.sigseed = trustee_seed
    trustee_def.nym = trustee_signer.identifier
    trustee_def.verkey = trustee_signer.verkey

    steward_defs = []
    node_defs = []
    client_defs = []

    for node_num in range(nodeCountToInit):
        node_name = nodeNames[node_num]
        logger.info('Generating defs for %s', node_name)

        steward_seed = generateSeed()
        logger.info('Steward seed will be %s', steward_seed)
        steward_seed = steward_seed.encode()    
        steward_signer = DidSigner(seed=steward_seed)
        steward_def = adict()
        steward_def.name = node_name + "-steward"
        steward_def.sigseed = steward_seed
        steward_def.nym = steward_signer.identifier
        steward_def.verkey = steward_signer.verkey
    
        client_seed = generateSeed()
        logger.info('Client seed will be %s', client_seed)
        client_seed = client_seed.encode()
        clent_signer = DidSigner(seed=client_seed)
        client_def = adict()
        client_def.name = node_name + "-client"
        client_def.sigseed = client_seed
        client_def.nym = clent_signer.identifier
        client_def.verkey = clent_signer.verkey

        node_seed = nodeSeeds[node_num]
        logger.info('Client seed will be %s', node_seed)
        node_seed = node_seed.encode()
        node_signer = Signer(node_seed)
        node_def = adict()
        node_def.name = node_name
        node_def.ip = nodeIps[node_num]
        node_def.port = args.node_port
        node_def.client_port = args.client_port
        node_def.sigseed = node_seed
        node_def.verkey = node_signer.verhex
        node_def.steward_nym = steward_signer.identifier

        steward_defs.append(steward_def)
        node_defs.append(node_def)
        client_defs.append(client_def)

    # 1. INIT DOMAIN LEDGER GENESIS FILE
    seq_no = 1
    trustee_txn = Member.nym_txn(trustee_def.nym, verkey=trustee_def.verkey, role=TRUSTEE,
                                    seq_no=seq_no,
                                    protocol_version=genesis_protocol_version)
    seq_no += 1
    domainLedger.add(trustee_txn)

    for node_num in range(nodeCountToInit):
        nym_txn = Member.nym_txn(steward_defs[node_num].nym, verkey=steward_defs[node_num].verkey, role=STEWARD, creator=trustee_def.nym,
                                        seq_no=seq_no,
                                        protocol_version=genesis_protocol_version)
        seq_no += 1
        domainLedger.add(nym_txn)

        # Trustee client
        txn = Member.nym_txn(client_defs[node_num].nym, verkey=client_defs[node_num].verkey, creator=client_defs[node_num].nym,
                                seq_no=seq_no,
                                protocol_version=genesis_protocol_version)
        seq_no += 1
        domainLedger.add(txn)

    # 2. INIT KEYS AND POOL LEDGER GENESIS FILE
    seq_no = 1

    for node_num in range(nodeCountToInit):    
        _, verkey, blskey, key_proof = initNodeKeysForBothStacks(node_defs[node_num].name, keys_dir, node_defs[node_num].sigseed, override=True)
        verkey = verkey.encode()
        assert verkey == node_defs[node_num].verkey

        nodeParamsFileName = 'indy.env'

        paramsFilePath = os.path.join(config.GENERAL_CONFIG_DIR, nodeParamsFileName)
        print('Nodes will not run locally, so writing {}'.format(paramsFilePath))
        TestNetworkSetup.writeNodeParamsFile(paramsFilePath, node_def.name,
                                            node_def.ip, node_def.port,
                                            node_def.ip, node_def.client_port)

        print("This node with name {} will use ports {} and {} for nodestack and clientstack respectively"
                .format(node_defs[node_num].name, node_defs[node_num].port, node_defs[node_num].client_port))

        node_nym = hexToFriendly(verkey)

        node_txn = Steward.node_txn(node_defs[node_num].steward_nym, node_defs[node_num].name, node_nym,
                                        node_defs[node_num].ip, node_defs[node_num].port, node_defs[node_num].client_port, blskey=blskey,
                                        bls_key_proof=key_proof,
                                        seq_no=seq_no,
                                        protocol_version=genesis_protocol_version)
        seq_no += 1
        poolLedger.add(node_txn)

    poolLedger.stop()
    domainLedger.stop()
