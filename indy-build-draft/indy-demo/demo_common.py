import json
import os
import string
import asyncio
import random

from indy import ledger, did, wallet, pool, error, crypto

pool_name = os.getenv('POOL_NAME', 'MESH')

async def create_and_open_pool(name: str, genesis_path: str):
    print('Opening ' + pool_name + ' pool')
    config = json.dumps({"genesis_txn": str(genesis_path)})

    try:
        await pool.delete_pool_ledger_config(config_name=name)
    except error.IndyError:
        pass

    await pool.set_protocol_version(2)

    await pool.create_pool_ledger_config(config_name=name, config=config)

    return await pool.open_pool_ledger(name, None)

class Agent():
    def __init__(self, pool_handle, wallet_name, wallet_key):
        self.wallet = None
        self.wallet_name = wallet_name
        self.wallet_key = wallet_key
        self.verinym_did = None
        self.verinym_key = None
        self.pool_handle = pool_handle

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._open_wallet())

    async def _open_wallet(self):
        print("Opening the wallet")

        config  = json.dumps({"id": self.wallet_name})
        creds = json.dumps({"key": self.wallet_key})

        try:
            await wallet.delete_wallet(config , creds)
        except error.IndyError:
            pass

        await wallet.create_wallet(config, creds)
        self.wallet = await wallet.open_wallet(config, creds)

    # def __del__(self):
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(wallet.close_wallet(self.wallet))

    async def create_did(self):
        return await did.create_and_store_my_did(self.wallet, "{}")

    async def fetch_key_by_did(self, _did):
        return await did.key_for_did(self.pool_handle, self.wallet, _did)

    async def store_did(self, new_did, new_key):
        req = await ledger.build_nym_request(self.verinym_did, new_did, new_key, None, None)
        await ledger.sign_and_submit_request(self.pool_handle, self.wallet, self.verinym_did, req)

class Connection():
    max_nonce = 1e7
    name_max_len = 6

    def __init__(self, pairwise_my_did, pairwise_my_key):
        self.name = ''.join(random.choices(string.ascii_letters, k = self.name_max_len))
        self.nonce = random.randint(0, self.max_nonce)
        self.authenticated = False
        self.verinym_did = None
        self.verinym_key = None
        self.pairwise_my_did = pairwise_my_did
        self.pairwise_my_key = pairwise_my_key
        self.pairwise_thier_key = None
        self.pairwise_thier_did = None

