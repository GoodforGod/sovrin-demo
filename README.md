# Indy-Agent Demo

In this demo we will be working with [indy-agent](https://github.com/hyperledger/indy-agent) repository. It provides hyperleger network and several agent with different roles.

We will be looking at Alice, Faber University and Acme Corporation agents. The story behind these agents is that Alice has graduated from Faber and wants to apply for a job at Acme. Since Acme requires a transcript from any trusted universities, including Faber, the following should happen:

1. Alice requests Faber to issue a transcript for her,
2. Faber issues transcript for Alice,
3. Acme request a transcript from Alice,
4. Alice send her transcript to Acme,
5. Acme validates that the transcript is issued by Faber.

## Initialization 

Clone demo repository and build container images:

```bash
git clone https://github.com/hyperledger/indy-agent
cd indy-agent/nodejs
docker-compose build
```

## Deployment

Deploy indy-node network and ingy agents:

```
docker-compose up
```

After that, the following container infrastructure will be deployied:

```bash
# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                              NAMES
d1cb85956c56        indy-agentjs        "bash -c 'npm start'"    20 hours ago        Up 3 seconds        0.0.0.0:3001->3001/tcp, 8000/tcp   nodejs_bob_1
87cbef41124f        indy-agentjs        "bash -c 'npm start'"    20 hours ago        Up 3 seconds        0.0.0.0:3004->3004/tcp, 8000/tcp   nodejs_thrift_1
7d268238f796        indy-agentjs        "bash -c 'npm start'"    20 hours ago        Up 2 seconds        0.0.0.0:3002->3002/tcp, 8000/tcp   nodejs_faber_1
28adc5a93399        indy-agentjs        "bash -c 'npm start'"    20 hours ago        Up 2 seconds        0.0.0.0:3003->3003/tcp, 8000/tcp   nodejs_acme_1
dc4f6e7dd38e        indy-agentjs        "bash -c 'npm start'"    20 hours ago        Up 6 seconds        0.0.0.0:3000->3000/tcp, 8000/tcp   nodejs_alice_1
64e77808cf01        nodejs_pool         "/usr/bin/supervisord"   20 hours ago        Up 6 seconds        0.0.0.0:9701-9708->9701-9708/tcp   nodejs_pool_1
```

`nodejs_pool` container runs 4 hyperledger blockchain nodes inside of it. There are also multiple agents build from `indy-agentjs` image and avaliable at the following endpoints:

* `http://localhost:3000/` for Alice
* `http://localhost:3001/` for Bob
* `http://localhost:3002/` for Faber University
* `http://localhost:3003/` for Acme Corporation
* `http://localhost:3004/` for Thrift Bank

## Usage

**Please note that these web pages do not update in real-time and you must refresh the page manually to check the result of any of your actions**

### Login to agents:

* Login to Alice agent (`localhost:3000`) with `alice` login and `123` password
* Login to Faber agent (`localhost:3002`) with `faber` login and `123` password
* Login to Acme agent (`localhost:3003`) with `acme` login and `123` password

![01-login](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/01-login.png?raw=true)

### Establish connection between Alice and Faber:

In Alice agent, press `Send New Connection Request`, enter Faber's DID endpoint (you can find in the bottom of Faber agent page) and send connection request:

![02-connection](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/02-connection.png?raw=true)

Then go to Messages page of both agents and accept "Proof Requests" for the name of each agent

![03-name-proof](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/03-name-proof.png?raw=true)

At this point you be able to see active connections with Alice in Faber agent and with Faber in Alice agent.

![04-rel](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/04-realationships.png?raw=true)

### Issue Transcript for Alice

In Faber agent, go to Issuing tab, create Transcript Schema, Credential Definition and send Credential Offer for Alice:

![05-creds](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/05-creds.png?raw=true)

In Alice agent, accept credential offer in Messages tab:

![06-offer](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/06-cred-offer.png?raw=true)

After that, in Alice agent in 'Credentials' tab you would see her transcript:

![07-creds](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/07-creds.png?raw=true)

### Establish connection between Alice and Acme agents

The process is similar as for Alice and Faber.

![08-acme](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/08-acme.png?raw=true)

### Send proof request

In Faber agent open Proof Requests tab, choose Transcript-Data and copy proof request:

![09-proof-req](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/09-proof-req-1.png?raw=true)

In Acme agent open Proof Requests tab, choose "Other (Paste Proof Request Here)", paste proof request and click Submit Query to send proof request:

![10-proof-req](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/10-proof-req-2.png?raw=true)

In Alice agent open Messages tab and accept the proof request:

![11-proof-req](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/11-proof-req-3.png?raw=true)

At this point Acme would receive Alice's transcript and would be able to validate it. You can check that in Acme agent by clicking on Alice relationship and then on 'Validate' button on the transcript proof:

![12-validate](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/12-validate.png?raw=true)

# Connection establishment protocol

Based on [getting started guide](https://github.com/hyperledger/indy-sdk/blob/master/doc/getting-started/getting-started.md) 

## DID Creation

`(did, verkey) = await did.create_and_store_my_did(wallet, "{}")`

Creates DID record in the wallet (local storage):

* `verkey` contains a public key
* `did` contains the first 16 bytes of the `verkey`
* Private key is stored in the wallet and cannot be accessed directly
* Optionally a random number generator seed can be provided 
* Source: https://github.com/hyperledger/indy-sdk/blob/ff1b106d8fe7fc7a3d704d2ff9af04e0b6a4d24b/libindy/src/api/did.rs#L55 

DID types:

1. A Verinym is associated with the Legal Identity of the Identity Owner.
2. Pseudonym - a Blinded Identifier used to maintain privacy in the context of an ongoing digital relationship (Connection). If the Pseudonym is used to maintain only one digital relationship we will call it a Pairwise-Unique Identifier.

## Connection Establishments Protocol

Suppose we have the following actors:

1. Steward. An organization with “Trust Anchor” role (i.e. it can assign “Trust Anchor” role to others and register DIDs).
2. Faber Collage (for consistency with Getting Started guide). An organization that wishes to establish connection with Steward

The following protocol for connection establishment is described in the guide:

Steward:

1. Steward already has DID (Verinym) stored in the Ledger. Let’s denote it by (S_did, S_key)
2. Creates new DID (Pseudonym) for communication with Faber (SF_did, SF_key)
3. Stores  (SF_did, SF_key) in the Ledger (creates NYM transaction (https://github.com/hyperledger/indy-node/blob/master/docs/requests.md#nym))
4. Creates Nonce – a random number.
5. Sends connection request containing SF_did and Nonce to Faber.

Faber:

1. Receives connection request
2. Creates new DID (Pseudonym) for communication with Steward (FS_did, FS_key)
3. Creates connection response containing (FS_did, FS_key, Nonce)
4. Fetches SF_key from the Ledger by Steward’s SF_did
5. Encrypts connection response with SF_key. By dong that Steward can verify the integrity of the message but it cannot identify the sender
6. Sends connection response

Steward:

1. Decrypts connection response with his private key
2. Compares Nonce from the connection response with the one created earlier. In case they match Faber is authenticated.
3. Stores Faber’s DID in the Ledger by creating NYM transaction with (S_did, FS_did, FS_key)

![conn-pseu](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/conn-pseu.png?raw=true)

At this point Faber is connected to the Steward and can interact in a secure peer-to-peer way. All parties must not use the same DID's to establish other relationships. By having independent pairwise relationships, you're reducing the ability for others to correlate your activities across multiple interactions.

The following protocol is described for creating Verinym DID after connection is established:

Faber:

1. Creates new DID (Verinym) denoted as (F_did, F_key).
2. Encrypts (F_did, F_key) with FS_key and  SF_key
3. By doing that Steward can verify both the integrity and the identity of the sender.
4. Sends encrypted message to Steward

Steward:

1. Decrypts the message, let’s denote Sender_key as a public key of this message
2. Fetches FS_key by FS_did from the Ledger. (I’m not sure if it’s required as Steward already has FS_key, also there’s an error in the guide compared to the code (https://github.com/hyperledger/indy-sdk/blob/28f34ef292c9cf22ed8c231d7fecb841857a3b8e/samples/python/src/getting_started.py#L798))
3. Compares Sender_key with FS_key. 
4. Creates the entry in the Ledger containing (F_did, F_key) and Faber’s roles (NYM transaction).

![conn-ver](https://github.com/apspdfoknd/sovrin-demo/blob/master/images/conn-ver.png?raw=true)

# Useful links

* [Sovrin whitepaper](https://sovrin.org/wp-content/uploads/Sovrin-Protocol-and-Token-White-Paper.pdf)
* [Indy-Node repository](https://github.com/hyperledger/indy-node)
* [Indy-SDK repository](https://github.com/hyperledger/indy-sdk)
* [Indy-Agent repository](https://github.com/hyperledger/indy-agent)
* [How to start pool](https://github.com/hyperledger/indy-sdk/blob/master/README.md#how-to-start-local-nodes-pool-with-docker), [another one](https://github.com/hyperledger/indy-node/blob/master/environment/docker/pool/README.md)
* [Getting started guide](https://github.com/hyperledger/indy-sdk/blob/master/doc/getting-started/getting-started.md), [source code](https://github.com/hyperledger/indy-sdk/blob/28f34ef292c9cf22ed8c231d7fecb841857a3b8e/samples/python/src/getting_started.py)
* [List of How-To guides](https://github.com/hyperledger/indy-sdk/tree/master/doc/how-tos)

