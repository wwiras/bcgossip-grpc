
### Bandwidth testing 28 Apr 2024 on 9:41 am.

<code>
puluncode@cloudshell:~/bcgossip-grpc (stoked-cosine-415611)$ python automation/bcgossip-bwidth.py 1 k8sv2/bandwidth
Processing deploy-10nodes-10Mbps.yaml: Total replicas defined in YAML: 10
/home/puluncode/bcgossip-grpc/k8sv2/python-role.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes-10Mbps.yaml applied successfully!
All 10 pods are running in namespace default.
Selected pod for test 1: bcgossip10nodes10mbps-5b85db4bb9-qrzgh
Initiating gossip from 10.80.0.11

Received acknowledgment: Done propagate! 10.80.0.11 received: '2b987-cubaan10-1'

Gossip propagation complete.
Test 1 complete for deploy-10nodes-10Mbps.yaml.
Deployment deletion initiated for /home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes-10Mbps.yaml.
Waiting for all pods to terminate...
Waiting for all pods to terminate...
Waiting for all pods to terminate...
No pods found in the namespace, deletion confirmed.
Processing deploy-10nodes.yaml: Total replicas defined in YAML: 10
/home/puluncode/bcgossip-grpc/k8sv2/python-role.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes.yaml applied successfully!
All 10 pods are running in namespace default.
Selected pod for test 1: bcgossip10nodes-59c5b4f66b-xsbwj
Initiating gossip from 10.80.0.12

Received acknowledgment: Done propagate! 10.80.0.12 received: '8e936-cubaan10-1'

Gossip propagation complete.
Test 1 complete for deploy-10nodes.yaml.
Deployment deletion initiated for /home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes.yaml.
Waiting for all pods to terminate...
Waiting for all pods to terminate...
Waiting for all pods to terminate...
No pods found in the namespace, deletion confirmed.
Processing deploy-10nodes-30Mbps.yaml: Total replicas defined in YAML: 10
/home/puluncode/bcgossip-grpc/k8sv2/python-role.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml applied successfully!
/home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes-30Mbps.yaml applied successfully!
All 10 pods are running in namespace default.
Selected pod for test 1: bcgossip10nodes30mbps-857b75879c-dktg7
Initiating gossip from 10.80.1.27

Received acknowledgment: Done propagate! 10.80.1.27 received: 'de32a-cubaan10-1'

Gossip propagation complete.
Test 1 complete for deploy-10nodes-30Mbps.yaml.
Deployment deletion initiated for /home/puluncode/bcgossip-grpc/k8sv2/bandwidth/deploy-10nodes-30Mbps.yaml.
Waiting for all pods to terminate...
Waiting for all pods to terminate...
Waiting for all pods to terminate...
No pods found in the namespace, deletion confirmed.
puluncode@cloudshell:~/bcgossip-grpc (stoked-cosine-415611)$ kubectl get pod
No resources found in default namespace.

</code>