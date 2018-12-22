#!/usr/bin/python3.6

from xmlrpc.client import ServerProxy

import random
import os
import asyncio
import json
import base64
import string

from indy import ledger, did, wallet, pool, error, crypto
from pprint import pprint as pp

from demo_common import create_and_open_pool, Agent, Connection

endpoint = os.getenv('STEWARD_ENDPOINT', 'http://localhost:8080/')
pool_name = os.getenv('POOL_NAME', 'MESH')
pool_genesis_txn_path = os.getenv('GENESIS_TNX_PATH', '/var/lib/indy/genesis/MESH/pool_transactions_genesis')
wallet_name = os.getenv('WALLET_NAME', 'wallet_agent')
wallet_key = os.getenv('WALLET_KEY', 'key_agent')

async def process_request(con_req):
    (pw_my_did, pw_my_key) = await agent.create_did()

    con = Connection(pw_my_did, pw_my_key)
    con.name = con_req['name']
    con.nonce = con_req['nonce']
    con.pairwise_thier_did = con_req['did']
    con.pairwise_thier_key = await agent.fetch_key_by_did(con_req['did'])

    con_resp = json.dumps({
        'did': con.pairwise_my_did,
        'key': con.pairwise_my_key,
        'nonce': con.nonce,
    })

    print('Encrypting connection response:')
    pp(con_resp)

    con_resp_enc = await crypto.anon_crypt(con.pairwise_thier_key, con_resp.encode('utf-8'))
    con_resp_enc_b64 = base64.b64encode(con_resp_enc).decode('utf-8')

    return con, con_resp_enc_b64

loop = asyncio.get_event_loop()

pool_handle = loop.run_until_complete(create_and_open_pool(pool_name, pool_genesis_txn_path))

agent = Agent(pool_handle, wallet_name, wallet_key)

with ServerProxy(endpoint) as proxy:
    print('\nCalling request_connection()')
    con_req = proxy.request_connection()
    print('Recieved connection request:')
    pp(con_req)

    print('\n')
    connection, con_resp = loop.run_until_complete(process_request(con_req))

    print("Calling authenticate_connection(" + connection.name + ", <encrypted>)")
    authenticated = proxy.authenticate_connection(connection.name, con_resp)
    print("Recieved authentication status:")
    pp(authenticated)

loop.run_until_complete(pool.close_pool_ledger(pool_handle))

loop.close()

