## Initialization 

```
git clone https://github.com/hyperledger/indy-agent
docker-compose build
```

## Usage

Deploy indy-node network and ingy agents:

```
docker-compose up
```

After that the following agents will be available:

* `http://localhost:3000/` for Alice
* `http://localhost:3002/` for Faber University
* `http://localhost:3003/` for Acme Corporation

> **Please note these web pages do not update in real-time and you must refresh the page manually to check the result of any of your actions**

### Login to agents:

1. Login to Alice agent (`localhost:3000`) with `alice` login and `123` password
2. Login to Faber agent (`localhost:3002`) with `faber` login and `123` password
3. Login to Acme agent (`localhost:3003`) with `acme` login and `123` password

### Establish connection between Alice and Faber:

1. in Alice agent, press `Send New Connection Request`
2. Enter Faber's DID endpoint (you can find in the bottom of Faber agent page)
3. Send connection request
4. Go to Messages page of both agents and accept "Proof Requests" for the name of each agent

At this point you be able to see active connection with Alice in Faber agent and with Faber in Alice agent.

### Issue Transcript for Alice

1. In Faber agent, go to Issuing tab
2. Create Transcript Schema
3. Create Credential Definition
4. Choose 'Alice' relationship and send her a Credential Offer
5. In Alice agent, accept credential offer in Messages tab

After that, in Alice agent in 'Credentials' tab you would see her transcript.

### Establish connection between Alice and Acme agents

The process is similar as for Alice and Faber.

### Send proof request

1. In Faber agent open Proof Requests tab, choose Transcript-Data and copy proof request
2. In Acme agent open Proof Requests tab, choose "Other (Paste Proof Request Here)" and paste proof request
3. Click Submit Query to send proof request
4. In Alice agent open Messages tab and accept the proof request

At this point Acme would receive Alice's transcript and would be able to validate it. You can check that in Acme agent by clicking on Alice relationship and then on 'Validate' button on the transcript proof.
