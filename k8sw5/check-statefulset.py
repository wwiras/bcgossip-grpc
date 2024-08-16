from kubernetes import client, config
import argparse  # Import the argparse module for handling command-line arguments

# Load Kubernetes configuration (usually from ~/.kube/config)
config.load_kube_config()

# Create API instance for interacting with StatefulSets
apps_v1 = client.AppsV1Api()

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Check the status of a Kubernetes StatefulSet.')

# Add an argument for the StatefulSet name
parser.add_argument('statefulsetname', type=str, help='The name of the StatefulSet to check.')

# Parse the arguments
args = parser.parse_args()

try:
    # Get the StatefulSet object using the provided name
    statefulset = apps_v1.read_namespaced_stateful_set(name=args.statefulsetname, namespace='default')

    # Check if all replicas are ready
    replicas = statefulset.status.replicas
    ready_replicas = statefulset.status.ready_replicas

    if replicas == ready_replicas:
        print(f"StatefulSet {args.statefulsetname} is OK (all {replicas} replicas ready).")
    else:
        print(f"StatefulSet {args.statefulsetname} has {ready_replicas} out of {replicas} replicas ready.")

except client.ApiException as e:
    print(f"Error getting StatefulSet status: {e}")