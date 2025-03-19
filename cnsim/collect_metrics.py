from google.cloud import monitoring_v3
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Initialize the Monitoring client
client = monitoring_v3.MetricServiceClient()

# project_id = "bcgossip-proj"
# location = "us-central1-c"
# cluster_name = "bcgossip-cluster"
# namespace_name = "default"

# Project details
project_id = "bcgossip-proj"  # Replace with your GCP project ID
project_name = f"projects/{project_id}"

# Define the time interval
def get_time_interval(start_time, end_time):
    """
    Creates a TimeInterval object for the given start and end times.
    """
    start_time_pb = Timestamp()
    start_time_pb.FromDatetime(start_time)

    end_time_pb = Timestamp()
    end_time_pb.FromDatetime(end_time)

    interval = monitoring_v3.TimeInterval()
    interval.start_time = start_time_pb
    interval.end_time = end_time_pb
    return interval

# Fetch metrics
def fetch_metrics(project_name, interval, metric_type):
    """
    Fetches metrics for the given time interval and metric type.
    """
    results = client.list_time_series(
        name=project_name,
        filter=f'metric.type = "{metric_type}"',
        interval=interval,
        view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    )
    print(f"results: {results}")
    return results

# Process and print metrics
def process_metrics(results, metric_name):
    """
    Processes the metrics data and prints it.
    """
    for result in results:
        print(f"Metric: {metric_name}")
        for point in result.points:
            timestamp = datetime.fromtimestamp(point.interval.start_time.seconds)
            if metric_name == "cpu_usage":
                value = point.value.double_value * 100  # Convert to percentage
            elif metric_name == "network_received_bytes":
                value = point.value.int64_value
            print(f"  Timestamp: {timestamp}, Value: {value}")

# Main function
if __name__ == "__main__":
    # Define the time range
    start_time = datetime(2025, 3, 19, 11, 42)  # Replace with your start time
    end_time = datetime(2025, 3, 19, 11, 45)    # Replace with your end time
    interval = get_time_interval(start_time, end_time)

    # Fetch and print CPU usage
    cpu_results = fetch_metrics(project_name, interval, "kubernetes.io/container/cpu/core_usage_time")
    process_metrics(cpu_results, "cpu_usage")

    # Fetch and print network received bytes
    network_results = fetch_metrics(project_name, interval, "kubernetes.io/pod/network/received_bytes_count")
    process_metrics(network_results, "network_received_bytes")
