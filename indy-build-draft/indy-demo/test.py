#!/usr/bin/python3.6

import json
import asyncio

from indy import ledger, did, wallet, pool, error, crypto
from pprint import pprint as pp

pool_genesis_txn_path = '/var/lib/indy/genesis/MESH/pool_transactions_genesis'

async def create_and_open_pool(name: str):
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    try:
        await pool.delete_pool_ledger_config(config_name=name)
    except error.IndyError:
        pass

    await pool.set_protocol_version(2)

    await pool.create_pool_ledger_config(config_name=name, config=pool_config)

    handle = await pool.open_pool_ledger(name, None)
    print("pool " + name + " is opened")

    return handle

async def create_and_open_wallet(name: str, key: str):
    config  = json.dumps({"id": name})
    creds = json.dumps({"key": key})

    try:
        await wallet.delete_wallet(config , creds)
    except error.IndyError:
        pass

    await wallet.create_wallet(config, creds)
    handle = await wallet.open_wallet(config, creds)

    print("wallet " + name + " is opened")

    return handle

async def submit_nym(pool_handle, from_wallet, from_did: str, new_did: str):
    req = await ledger.build_nym_request(from_did, new_did, None, None, None)
    await ledger.sign_and_submit_request(pool_handle, from_wallet, from_did, req)


async def send_nym(pool_handle, _wallet, _did, new_did, new_key, role):
    nym_request = await ledger.build_nym_request(_did, new_did, new_key, None, role)
    await ledger.sign_and_submit_request(pool_handle, _wallet, _did, nym_request)
    print("sybmit NYM from: " + _did + " new: " + new_did)

async def get_nym(pool_handle, from_did, get_did):
    req = await ledger.build_get_nym_request(from_did, get_did)
    resp = await ledger.submit_request(pool_handle, req)
    resp = json.loads(resp)

    print("get NYM from: " + from_did + " get:"  + get_did)
    print("fetched DID: " + resp['result']['dest'])

    return resp

async def auth_decrypt(wallet_handle, key, message):
    from_verkey, decrypted_message_json = await crypto.auth_decrypt(wallet_handle, key, message)
    decrypted_message_json = decrypted_message_json.decode("utf-8")
    decrypted_message = json.loads(decrypted_message_json)
    return from_verkey, decrypted_message_json, decrypted_message


async def main():
    pool_handle = await create_and_open_pool("MESH")

    s_wallet = await create_and_open_wallet("s_wallet", "aa")
    f_wallet = await create_and_open_wallet("f_wallet", "aa")

    steward_did_info = {'seed': 'V8uywXJVAjo1wZWPq818QafckMfno2BB'}
    (s_did, s_key) = await did.create_and_store_my_did(s_wallet, json.dumps(steward_did_info))

    (sf_did, sf_key) = await did.create_and_store_my_did(s_wallet, "{}")

    con_req = {
        'did': sf_did,
        'nonce': 123456789
    }

    await send_nym(pool_handle, s_wallet, s_did, sf_did, sf_key, None)

    (fs_did, fs_key) = await did.create_and_store_my_did(f_wallet, "{}")

    assert sf_key == await did.key_for_did(pool_handle, f_wallet, con_req['did'])

    con_resp = json.dumps({
        'did': fs_did,
        'key': fs_key,
        'nonce': con_req['nonce']
    })

    con_resp_enc = await crypto.anon_crypt(sf_key, con_resp.encode('utf-8'))

    con_resp_dec = \
        json.loads((await crypto.anon_decrypt(s_wallet, sf_key,
                                            con_resp_enc)).decode("utf-8"))

    assert con_resp_dec['nonce'] == con_req['nonce']

    await send_nym(pool_handle, s_wallet, s_did, fs_did, fs_key, None)

    print("connection established")

    # == to
    (f_did, f_key) = await did.create_and_store_my_did(f_wallet, "{}")

    f_info = json.dumps({
        'did': f_did,
        'key': f_key
    })

    f_info_enc = await crypto.auth_crypt(f_wallet, fs_key, sf_key, f_info.encode('utf-8'))

    sender_key, f_info_dec_json, f_info_dec = \
        await auth_decrypt(s_wallet, sf_key, f_info_enc)

    assert sender_key == await did.key_for_did(pool_handle, s_wallet, fs_did)

    await send_nym(pool_handle, s_wallet, s_did, f_info_dec['did'], f_info_dec['key'], None)

    (a_did, a_verkey) = await did.create_and_store_my_did(a_wallet, "{}")
    (b_did, b_verkey) = await did.create_and_store_my_did(b_wallet, "{}")

    print("a DID: " + a_did)
    print("b DID: " + b_did)

    await did.store_their_did(a_wallet, json.dumps({'did': b_did, 'verkey': b_verkey}))
    await did.store_their_did(steward_wallet, json.dumps({'did': b_did, 'verkey': b_verkey}))
    await did.store_their_did(b_wallet, json.dumps({'did': steward_did, 'verkey': steward_key}))

    await send_nym(pool_handle, b_wallet, b_did, a_did)
    await submit_nym(pool_handle, steward_wallet, steward_did, b_did)

    nym = await get_nym(pool_handle, b_did, a_did)
    pp(nym)

    await wallet.close_wallet(b_wallet)
    await wallet.close_wallet(a_wallet)
    await pool.close_pool_ledger(pool_handle)

    print("done")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
