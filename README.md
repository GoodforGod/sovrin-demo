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

# Useful links

* [Sovrin whitepaper](https://sovrin.org/wp-content/uploads/Sovrin-Protocol-and-Token-White-Paper.pdf)
* [Indy-Node repository](https://github.com/hyperledger/indy-node)
* [Indy-SDK repository](https://github.com/hyperledger/indy-sdk)
* [Indy-Agent repository](https://github.com/hyperledger/indy-agent)
* [How to start pool](https://github.com/hyperledger/indy-sdk/blob/master/README.md#how-to-start-local-nodes-pool-with-docker), [another one](https://github.com/hyperledger/indy-node/blob/master/environment/docker/pool/README.md)
* [Getting started guide](https://github.com/hyperledger/indy-sdk/blob/master/doc/getting-started/getting-started.md), [source code](https://github.com/hyperledger/indy-sdk/blob/28f34ef292c9cf22ed8c231d7fecb841857a3b8e/samples/python/src/getting_started.py)

