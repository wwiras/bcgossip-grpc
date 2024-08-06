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

# Define column data types for BigQuery
dtypes = {
    'message': 'STRING',
    'sender_id': 'STRING',
    'receiver_id': 'STRING',
    'received_timestamp': 'TIMESTAMP',
    'propagation_time': 'FLOAT64',
    'event_type': 'STRING'
}

# Create dataframe
df = pd.DataFrame(data)

# Change data types to match
for col in df.columns:
    if col in dtypes:
        df[col] = df[col].astype(dtypes[col])

# Specify the table you want to upload to
table_id = "gossip_simulation.gossip_events"

try:
    # Upload the DataFrame to BigQuery
    pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='append', table_schema=dtypes)
    print(f"Data uploaded to {project_id}.{table_id} successfully.")

except pandas_gbq.gbq.GenericGBQException as e:
    print(f"Error uploading to BigQuery: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
