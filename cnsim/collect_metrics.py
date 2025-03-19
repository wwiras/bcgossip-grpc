from google.cloud import monitoring_v3
import datetime

def get_network_received_bytes(project_id, location, cluster_name, namespace_name, nodes, start_time, end_time):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    start_time_pb = monitoring_v3.Timestamp()
    start_time_pb.seconds = int(start_time.timestamp())
    start_time_pb.nanos = int((start_time.timestamp() - int(start_time.timestamp())) * 10**9)

    end_time_pb = monitoring_v3.Timestamp()
    end_time_pb.seconds = int(end_time.timestamp())
    end_time_pb.nanos = int((end_time.timestamp() - int(end_time.timestamp())) * 10**9)

    interval = int((end_time - start_time).total_seconds())

    query = f"""
        sum(rate(kubernetes_io:pod_network_received_bytes_count{{
            monitored_resource="k8s_pod",
            project_id="{project_id}",
            location="{location}",
            cluster_name="{cluster_name}",
            namespace_name="{namespace_name}",
            nodes="{nodes}"
        }}[{interval}s]))
    """

    request = {
        "name": project_name,
        "query": query,
        "time_range": {"start_time": start_time_pb, "end_time": end_time_pb},
    }

    results = client.query_time_series(request)

    for result in results:
        for point in result.points:
            return point.value.double_value

    return 0.0

if __name__ == "__main__":
    project_id = "bcgossip-proj"
    location = "us-central1-c"
    cluster_name = "bcgossip-cluster"
    namespace_name = "default"

    test_runs = [
        {"nodes": "10", "start": datetime.datetime(2025, 3, 19, 11, 45), "end": datetime.datetime(2025, 3, 19, 11, 42)},
        {"nodes": "30", "start": datetime.datetime(2025, 3, 19, 11, 49), "end": datetime.datetime(2025, 3, 19, 11, 45)},
    ]

    print("Nodes, Network Received Bytes (rate)")
    for test_run in test_runs:
        network_bytes = get_network_received_bytes(project_id, location, cluster_name, namespace_name, test_run["nodes"], test_run["start"], test_run["end"])
        print(f"{test_run['nodes']}, {network_bytes}")