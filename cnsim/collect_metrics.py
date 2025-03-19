from google.cloud import monitoring_v3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time

def get_and_plot_metrics(project_id, metric_type, resource_labels, start_time, end_time, plot_title="Metrics Plot"):
    """
    Retrieves and plots metrics data from Google Cloud Monitoring.

    Args:
        project_id: GCP project ID.
        metric_type: Metric type (e.g., "compute.googleapis.com/instance/cpu/usage_time").
        resource_labels: Dictionary of resource labels for filtering.
        start_time: datetime object for the start of the time interval.
        end_time: datetime object for the end of the time interval.
        plot_title: Title of the plot.
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    interval = monitoring_v3.TimeInterval()
    interval.start_time = monitoring_v3.Timestamp(seconds=int(start_time.timestamp()))
    interval.end_time = monitoring_v3.Timestamp(seconds=int(end_time.timestamp()))

    filter_str = f'metric.type = "{metric_type}"'
    for key, value in resource_labels.items():
        filter_str += f' AND resource.labels.{key} = "{value}"'

    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": filter_str,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
    except Exception as e:
        print(f"Error retrieving metrics: {e}")
        return

    time_list_x_axis = []
    utilization_list_y_axis = []

    for result in results:
        for point in result.points:
            time_list_x_axis.append(datetime.datetime.fromtimestamp(point.interval.start_time.seconds))
            utilization_list_y_axis.append(point.value.double_value * 100)

    if not time_list_x_axis:
        print("No data points found for the given time interval and filters.")
        return

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(time_list_x_axis, utilization_list_y_axis, color='lightblue', linewidth=2)
    fig.set_size_inches(20.5, 14.5)

    xfmt = mdates.DateFormatter('%B/%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.title(plot_title)
    plt.xlabel("Time")
    plt.ylabel("Utilization (%)")
    plt.show()

if __name__ == "__main__":
    # project_id = "bcgossip-proj"
    # location = "us-central1-c"
    # cluster_name = "bcgossip-cluster"
    # namespace_name = "default"

    project_id = "bcgossip-proj"  # Replace with yours
    metric_type = "compute.googleapis.com/instance/cpu/usage_time"
    resource_labels = {"cluster_name": "bcgossip-cluster"}  # Replace with your labels
    # start_time = datetime.datetime(2021, 6, 1, 2, 10, 23)
    # end_time = datetime.datetime(2021, 6, 1, 2, 15, 23)
    start_time = datetime.datetime(2025, 3, 19, 11, 42)
    end_time = datetime.datetime(2025, 3, 19, 11, 45)
    get_and_plot_metrics(project_id, metric_type, resource_labels, start_time, end_time)

