import argparse
from kubernetes import client, config
import iperf3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_pod_ip(pod_name, namespace="default"):
    """Fetches the IP address of a pod in the specified namespace."""
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.status.pod_ip

def perform_bandwidth_test(server_ip, duration=5):
    """Performs an iperf3 bandwidth test to the specified server IP."""

    # Set Iperf Client Options
    client = iperf3.Client()
    client.server_hostname = server_ip
    client.zerocopy = True
    client.verbose = False  # Set to True if you want more detailed iperf3 output
    client.reverse = True
    client.port = 5201
    client.num_streams = 10
    client.duration = int(duration)
    client.bandwidth = 1000000000

    try:
        # Run iperf3 test
        result = client.run()

        # Log the iperf3 command and its output (for debugging)
        logging.debug(f"iperf3 command: {client.get_command()}")
        if result.error:
            logging.error(f"iperf3 error: {result.error}")
        else:
            logging.debug(f"iperf3 output: {result.text}")

        # Extract and return bandwidth results if successful
        if not result.error:
            sent_mbps = int(result.sent_Mbps)
            received_mbps = int(result.received_Mbps)
            return sent_mbps, received_mbps
        else:
            return None, None  # Or some other default values indicating an error

    except iperf3.Iperf3Error as e:
        # Handle specific iperf3 errors
        logging.error(f"iperf3 error: {e}")
        return None, None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Perform a bandwidth test to a target pod.")
    parser.add_argument('--targetpod', required=True, help="Target pod's name to perform the bandwidth test against")
    parser.add_argument('--duration', type=int, default=5, help="Duration of the bandwidth test in seconds")
    args = parser.parse_args()

    server_ip = get_pod_ip(args.target_pod)

    current_time = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')

    print(f"Time: {current_time}")
    print(f"Connecting to host {server_ip}, port 5201")

    # Extract the bandwidth (sent_mbps, received_mbps) from the result
    sent_mbps, received_mbps = perform_bandwidth_test(server_ip, args.duration)

    # Print the bandwidth result or an error message
    if sent_mbps is not None and received_mbps is not None:
        print(f'sent_mbps: {sent_mbps}', flush=True)
        print(f'received_mbps: {received_mbps}', flush=True)
    else:
        print("Bandwidth test failed. Check the logs for details.")
