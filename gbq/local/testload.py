import pandas_gbq
import pandas as pd

# Set your project ID (replace 'your-project-id')
project_id = "bcgossip-proj"

# Create a dummy DataFrame (new data)
data = {
    'message': ['Greetings!', 'What\'s up?', 'Have a nice day!'],
    'sender_id': ['node-A', 'node-B', 'node-C'],
    'receiver_id': ['node-D', 'node-E', 'node-F'],
    'received_timestamp': [
        pd.Timestamp.now(),
        pd.Timestamp.now() - pd.Timedelta(hours=2),
        pd.Timestamp.now() - pd.Timedelta(days=1)
    ],
    'propagation_time': [0.2, 0.7, 1.5],
    'event_type': ['RECEIVE', 'SEND', 'SEND']
}

# Create dataframe
df = pd.DataFrame(data)

# Change data types to match (modified)
for col in df.columns:
    if col == 'received_timestamp':
        df[col] = pd.to_datetime(df[col])

# Specify the table you want to upload to
table_id = "gossip_simulation.gossip_events_new"  # Use the same table you created earlier

try:
    # Upload the DataFrame to BigQuery, appending to existing table
    pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='append')
    print(f"Data appended to {project_id}.{table_id} successfully.")

except pandas_gbq.gbq.GenericGBQException as e:
    print(f"Error uploading to BigQuery: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

