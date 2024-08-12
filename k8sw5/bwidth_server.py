import iperf3
import socket
from kubernetes import client, config
import os

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

    # Get the port number from the environment variable or default to 5201
    server.port = int(os.environ.get('IPERF_SERVER_PORT', 5201))

    pod_name = socket.gethostname()
    pod_ip = get_pod_ip(pod_name)

    print(f"Pod Name: {pod_name}",flush=True)
    print(f"Pod IP: {pod_ip}",flush=True)
    print(f'iperf3 server is running on port {server.port}...',flush=True)

    try:
        server.run()
    except iperf3.Iperf3Error as e:
        print(f"Error running iperf3 server: {e}",flush=True)

if __name__ == '__main__':
    run_iperf3_server()
