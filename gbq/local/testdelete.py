from google.cloud import bigquery

# Set your project ID
project_id = 'bcgossip-proj'
table_id = 'gossip_events'

# Construct the delete query
delete_query = """
DELETE FROM `bcgossip-proj.gossip_simulation.gossip_events` 
WHERE event_type = 'SEND'
"""

# Create a BigQuery client
client = bigquery.Client(project=project_id)

try:
    # Execute the query
    query_job = client.query(delete_query)
    query_job.result()  # Wait for the jobs to complete

    print(f"Rows with event_type='SEND' deleted from table {table_id}")

except Exception as e:
    print(f"Error deleting rows: {e}")
