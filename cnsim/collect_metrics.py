import time
import json
from google.cloud import monitoring_v3
import datetime
from google.protobuf.timestamp_pb2 import Timestamp

def get_network_received_bytes(project_id, location, cluster_name, namespace_name, nodes, start_time, end_time):
    """
    Fetches the network received bytes for a specific pod in a Kubernetes cluster.
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    # Convert datetime to Timestamp
    start_time_pb = Timestamp()
    start_time_pb.FromDatetime(start_time)

    end_time_pb = Timestamp()
    end_time_pb.FromDatetime(end_time)

    # Define the time interval
    interval = monitoring_v3.TimeInterval()
    interval.start_time = start_time_pb
    interval.end_time = end_time_pb

    # Define the metric filter
    metric_type = "kubernetes.io/pod/network/received_bytes_count"
    filter_str = (
        f'metric.type="{metric_type}" '
        f'AND resource.labels.project_id="{project_id}" '
        f'AND resource.labels.location="{location}" '
        f'AND resource.labels.cluster_name="{cluster_name}" '
        f'AND resource.labels.namespace_name="{namespace_name}" '
        f'AND resource.labels.pod_name=~"gossip-statefulset-.*"'
    )

    # Query the metric
    results = client.list_time_series(
        name=project_name,
        filter=filter_str,
        interval=interval,
        view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    )

    # Process the results
    total_received_bytes = 0
    for result in results:
        for point in result.points:
            total_received_bytes += point.value.int64_value

    return total_received_bytes

if __name__ == "__main__":
    project_id = "bcgossip-proj"
    location = "us-central1-c"
    cluster_name = "bcgossip-cluster"
    namespace_name = "default"

    # Define test runs with correct time ranges
    test_runs = [
        {"nodes": "10", "start": datetime.datetime(2025, 3, 19, 11, 42), "end": datetime.datetime(2025, 3, 19, 11, 45)},
        {"nodes": "30", "start": datetime.datetime(2025, 3, 19, 11, 46), "end": datetime.datetime(2025, 3, 19, 11, 49)},
    ]

    print("Nodes, Network Received Bytes")
    for test_run in test_runs:
        network_bytes = get_network_received_bytes(
            project_id, location, cluster_name, namespace_name, test_run["nodes"], test_run["start"], test_run["end"]
        )
        print(f"{test_run['nodes']}, {network_bytes}")