#!/usr/bin/python3.6

from xmlrpc.server import SimpleXMLRPCServer
import random
import os
import asyncio
import json
import sys
import base64
import string

from indy import ledger, did, wallet, pool, error, crypto
from pprint import pprint as pp

from demo_common import create_and_open_pool, Agent, Connection

rpc_port = os.getenv('PORT', 8080)

pool_name = os.getenv('POOL_NAME', 'MESH')
pool_genesis_txn_path = os.getenv('GENESIS_TNX_PATH', '/var/lib/indy/genesis/MESH/pool_transactions_genesis')
wallet_name = os.getenv('WALLET_NAME', 'wallet_steward')
wallet_key = os.getenv('WALLET_KEY', 'key_steward')

connections = {}

class Steward(Agent):
    did_seed = os.getenv('DID_KEY', 'V8uywXJVAjo1wZWPq818QafckMfno2BB')

    def __init__(self, pool_handle, wallet_name, wallet_key):
        super().__init__(pool_handle, wallet_name, wallet_key)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._recover_did())

    async def _recover_did(self):
        did_info = json.dumps({'seed': self.did_seed})
        (self.verinym_did, self.verinym_key) = \
            await did.create_and_store_my_did(self.wallet, did_info)

        print("Steward Verinym DID: " + self.verinym_did)

async def request_connection():
    (pw_my_did, pw_my_key) = await steward.create_did()

    await steward.store_did(pw_my_did, pw_my_key)

    con = Connection(pw_my_did, pw_my_key)

    connections[con.name] = con

    return {
        'name': con.name,
        'did': con.pairwise_my_did,
        'nonce': con.nonce
    }

async def authenticate_connection(name, con_resp_enc_b64):
    if name not in connections:
        return {'authenticated': False, 'error': 'unknown name'}

    con = connections[name]

    con_resp_enc = base64.b64decode(con_resp_enc_b64.encode('utf-8'))

    con_resp_dec = json.loads((await crypto.anon_decrypt(steward.wallet, con.pairwise_my_key,
                                            con_resp_enc)).decode("utf-8"))

    if con_resp_dec['nonce'] != con.nonce:
        return {'authenticated': False, 'error': 'wrong nonce'}

    print('Decrypted connection responce:')
    pp(con_resp_dec)

    con.pairwise_thier_did = con_resp_dec['did']
    con.pairwise_thier_key = con_resp_dec['key']

    await steward.store_did(con.pairwise_thier_did, con.pairwise_thier_key)

    con.authenticated = True

    return {'authenticated': True}

def api_request_connection():
    print("\nCalled request_connection()")

    con_req = loop.run_until_complete(request_connection())

    print("Sending new connection request:")
    pp(con_req)

    return con_req


def api_authenticate_connection(name, con_resp_enc):
    print("\nCalled authenticate_connection(" + name + ", <encrypted>)")

    authenticated = loop.run_until_complete(authenticate_connection(name, con_resp_enc))

    print("Sending authentication status:")
    pp(authenticated)

    return authenticated

loop = asyncio.get_event_loop()

pool_handle = loop.run_until_complete(create_and_open_pool(pool_name, pool_genesis_txn_path))

steward = Steward(pool_handle, wallet_name, wallet_key)

server = SimpleXMLRPCServer(('0.0.0.0', rpc_port), logRequests=False)
server.register_function(api_request_connection, "request_connection")
server.register_function(api_authenticate_connection, "authenticate_connection")

print('Serving on {}'.format(rpc_port))
server.serve_forever()

loop.run_until_complete(pool.close_pool_ledger(pool_handle))

loop.close()

