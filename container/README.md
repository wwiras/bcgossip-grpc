
# Container(docker) environment - gRPC
1. Go to "container" directory. Running all container with docker-compose. 
```shell
~/bcgossip-grpc/container$ sudo docker-compose up -d
[+] Building 11.9s (17/21)                                                                                                   docker:default
 => [node2 internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 666B                                                                                                   0.0s
 => [node2 internal] load .dockerignore                                                                                                0.0s
 => => transferring context: 2B                                                                                                        0.0s
 => [node1 internal] load metadata for docker.io/library/python:3.11-slim                                                              3.9s
 => [node1 internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 666B                                                                                                   0.0s
 => [node1 internal] load .dockerignore                                                                                                0.0s
 => => transferring context: 2B                                                                                                        0.0s
 => [node3 internal] load build definition from Dockerfile                                                                             0.0s
 => => transferring dockerfile: 666B                                                                                                   0.0s
 => [node3 internal] load .dockerignore                                                                                                0.0s
 => => transferring context: 2B                                                                                                        0.0s
 => [node3 1/4] FROM docker.io/library/python:3.11-slim@sha256:ce81dc539f0aedc9114cae640f8352fad83d37461c24a3615b01f081d0c0583a        2.7s
 => => resolve docker.io/library/python:3.11-slim@sha256:ce81dc539f0aedc9114cae640f8352fad83d37461c24a3615b01f081d0c0583a              0.0s
 => => sha256:07b3e0dc751aaf60f7e8329edf7332166d9dbfdf7ab0405420d860c46146c881 12.84MB / 12.84MB                                       2.0s
 => => sha256:7e0115596a7a4e49d1034304974dbd2a675dfdee9df8da9437f913a614fef819 244B / 244B                                             0.6s
 => => sha256:a66610a3b2a1b945b6e139a56387e83f06b835b82feedca0729d2381d0c733fa 3.41MB / 3.41MB                                         1.4s
 => => sha256:ce81dc539f0aedc9114cae640f8352fad83d37461c24a3615b01f081d0c0583a 1.65kB / 1.65kB                                         0.0s
 => => sha256:238b008604c229d4897d1fa131f9aaecddec61a199edbdb22851622dd65dcebd 1.37kB / 1.37kB                                         0.0s
 => => sha256:cfa17c2baa64b89de4e828d2f7f219dc88a61599b076ef7ea08c653f6df56b74 6.95kB / 6.95kB                                         0.0s
 => => extracting sha256:07b3e0dc751aaf60f7e8329edf7332166d9dbfdf7ab0405420d860c46146c881                                              0.4s
 => => extracting sha256:7e0115596a7a4e49d1034304974dbd2a675dfdee9df8da9437f913a614fef819                                              0.0s
 => => extracting sha256:a66610a3b2a1b945b6e139a56387e83f06b835b82feedca0729d2381d0c733fa                                              0.2s
 => [node2 internal] load build context                                                                                                0.0s
 => => transferring context: 5.46kB                                                                                                    0.0s
 => [node1 internal] load build context                                                                                                0.0s
 => => transferring context: 5.46kB                                                                                                    0.0s
 => [node3 internal] load build context                                                                                                0.0s
 => => transferring context: 5.46kB                                                                                                    0.0s
 => [node3 2/4] WORKDIR /app                                                                                                           0.1s
 => [node3 3/4] COPY . /app                                                                                                            0.0s
 => [node3 4/4] RUN pip install --upgrade pip &&     pip install --no-cache-dir grpcio grpcio-tools                                    4.8s
 => [node1] exporting to image                                                                                                         0.2s 
 => => exporting layers                                                                                                                0.2s 
 => => writing image sha256:99da623cb8d02a06c1ed02ceb5d3d9fef83a0c7c06ecba045348e9a1629e5004                                           0.0s 
 => => naming to docker.io/library/container-node1                                                                                     0.0s 
 => [node3] exporting to image                                                                                                         0.2s 
 => => exporting layers                                                                                                                0.2s
 => => writing image sha256:978b43c550e57f3194e5eb87fa14eb16ac7b1a38faec7a23bf4213e2215efdfe                                           0.0s
 => => naming to docker.io/library/container-node3                                                                                     0.0s
 => [node2] exporting to image                                                                                                         0.2s
 => => exporting layers                                                                                                                0.1s
 => => writing image sha256:1bc7b0d59ee8a85f3d1c311ea3569223e72b99ff5ba0197c3602fc379f0929a6                                           0.0s
 => => naming to docker.io/library/container-node2                                                                                     0.0s
[+] Running 4/4
 ✔ Network container_gossip-net  Created                                                                                               0.1s 
 ✔ Container node3               Started                                                                                               0.0s 
 ✔ Container node1               Started                                                                                               0.0s 
 ✔ Container node2               Started                                                                                           
```
2. Verify all container (nodes) existance

```shell
~/bcgossip-grpc/container$ sudo docker ps -a
CONTAINER ID   IMAGE             COMMAND            CREATED          STATUS          PORTS      NAMES
70574c5c76dd   container-node1   "python node.py"   18 seconds ago   Up 17 seconds   5050/tcp   node1
7aae61ffdc64   container-node3   "python node.py"   18 seconds ago   Up 16 seconds   5050/tcp   node3
4868de087fcc   container-node2   "python node.py"   18 seconds ago   Up 16 seconds   5050/tcp   node2
```

3. Access one of the node containers
```shell
~/bcgossip-grpc/container$ sudo docker exec -it node1 sh
```

4. Initiate gossip with 3 arguments
```shell
$ python initiate.py --target_node node1 --message "Hello from the outside" --sender_id "init"            
Received acknowledgment: node1 received: 'Hello from the outside'
$ exit
```

5. Check logs of each nodes to verify
```shell
~/bcgossip-grpc/container$ sudo docker logs --details -t node1
2024-02-25T02:48:41.203393492Z  node1 listening on port 5050
2024-02-25T02:50:21.575363229Z  node1 received message: 'Hello from the outside' from init
2024-02-25T02:50:21.581878532Z  node1 received message: 'Hello from the outside' from node3
2024-02-25T02:50:21.582523329Z  node1 forwarded message to node2
2024-02-25T02:50:21.582994666Z  node1 forwarded message to node3
```

```shell
~/bcgossip-grpc/container$ sudo docker logs --details -t node2
2024-02-25T02:48:41.307693471Z  node2 listening on port 5050
2024-02-25T02:50:21.579137968Z  node2 received message: 'Hello from the outside' from node1
2024-02-25T02:50:21.582368161Z  node2 forwarded message to node3
```

```shell
~/bcgossip-grpc/container$ sudo docker logs --details -t node3
2024-02-25T02:48:41.387470815Z  node3 listening on port 5050
2024-02-25T02:50:21.581330361Z  node3 received message: 'Hello from the outside' from node2
2024-02-25T02:50:21.582020658Z  node3 forwarded message to node1
2024-02-25T02:50:21.582935583Z  node3 received message: 'Hello from the outside' from node1
```

6. Down and remove all docker instance
```bash
~/bcgossip-grpc/container$ sudo docker-compose down
[+] Running 4/4
 ✔ Container node3               Removed                                                                                              10.4s 
 ✔ Container node1               Removed                                                                                              10.6s 
 ✔ Container node2               Removed                                                                                              10.6s 
 ✔ Network container_gossip-net  Removed     
```
