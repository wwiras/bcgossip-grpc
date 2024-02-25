# bcgossip-grpc
Blockchain Gossip with gRPC communication

For local
1. Create virtual environment 
```bash
python3 -m venv venvlocal. 
```
Activate virtual environment

```bash
source venvlocal/bin/activate 
```


2. Running and up node
```bash
$ python node-noasyncio.py 1 5051 "localhost:5052,localhost:5053"
Node 1 listening on port 5051
```
```bash
$ python node-noasyncio.py 2 5052 "localhost:5051,localhost:5053"
Node 2 listening on port 5052
```
```bash
$ python node-noasyncio.py 3 5053 "localhost:5051,localhost:5052"
Node 3 listening on port 5053
```


3. Initiate gossip
```bash
$ python initiate.py  
Enter target node port: 5051  
Enter message to send: cubaan1  
Enter sender node ID: init  
Received acknowledgment: Node 1 received: 'cubaan1' from Node init
```


