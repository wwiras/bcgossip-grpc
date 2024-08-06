import pandas_gbq
import pandas as pd

# Set your project ID (replace 'your-project-id')
project_id = "bcgossip-proj"

# Create a dummy DataFrame (replace with your own data)
data = {
    'message': ['Hello', 'Good morning', 'How are you?'],
    'sender_id': ['gossip-statefulset-1', 'gossip-statefulset-2', 'gossip-statefulset-3'],
    'receiver_id': ['gossip-statefulset-4','gossip-statefulset-5', 'gossip-statefulset-6'],
    'received_timestamp': pd.Timestamp.now(),  # Current timestamp
    'propagation_time': [0.5, 0.8, 1.2],  # Example propagation times
    'event_type': ['SEND', 'SEND', 'RECEIVE']
}

# Create dataframe
df = pd.DataFrame(data)

# Specify a new table ID (replace with your desired table name)
table_id = "gossip_simulation.gossip_events"

# Define schema manually
schema = [
        {'name': 'message', 'type': 'STRING'},
        {'name': 'sender_id', 'type': 'STRING'},
        {'name': 'receiver_id', 'type': 'STRING'},
        {'name': 'received_timestamp', 'type': 'TIMESTAMP'},
        {'name': 'propagation_time', 'type': 'FLOAT'},
        {'name': 'event_type', 'type': 'STRING'},
    ]

try:
    # Upload the DataFrame to BigQuery, creating the table if it doesn't exist
    pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='fail', table_schema=schema)
    print(f"Data uploaded to {project_id}.{table_id} successfully.")

except pandas_gbq.gbq.GenericGBQException as e:
    print(f"Error uploading to BigQuery: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

