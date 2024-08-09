import iperf3
import socket
from kubernetes import client, config

def get_pod_ip(pod_name, namespace="default"):
    """Fetches the IP address of a pod in the specified namespace."""
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.status.pod_ip

def run_iperf3_server():
    """Runs an iperf3 server in the foreground."""

    server = iperf3.Server()
    server.verbose = False

    pod_name = socket.gethostname()
    pod_ip = get_pod_ip(pod_name)

    print(f"Pod Name: {pod_name}")
    print(f"Pod IP: {pod_ip}")
    print('iperf3 server is running...')

    server.run()

if __name__ == '__main__':
    run_iperf3_server()