import argparse
from kubernetes import client, config
import iperf3
from datetime import datetime

def get_pod_ip(pod_name, namespace="default"):
    """Fetches the IP address of a pod in the specified namespace."""
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.status.pod_ip

def perform_bandwidth_test(server_ip):
# def perform_bandwidth_test(server_ip, duration=10):

    """Performs an iperf3 bandwidth test to the specified server IP."""
    # client = iperf3.Client()
    # client.server_hostname = server_ip
    # client.zerocopy = True
    # client.verbose = False
    # client.port = 5201  # Default iperf3 server port
    # client.num_streams = 10
    # client.duration = int(duration)
    # client.bandwidth = 1000000000

    client = iperf3.Client()
    client.server_hostname = server_ip
    client.json_output = False

    result = client.run()

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Perform a bandwidth test to a target pod.")
    parser.add_argument('--target_pod', required=True, help="Target pod's name to perform the bandwidth test against")
    args = parser.parse_args()
    server_ip = get_pod_ip(args.target_pod)

    current_time = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')

    print(f"Time: {current_time}")
    print(f"Connecting to host {server_ip}, port 5201")

    # result = perform_bandwidth_test(server_ip, args.duration)
    result = perform_bandwidth_test(server_ip)

    # print(result.text)
    print(result)
