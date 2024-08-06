from google.cloud import bigquery

def create_table(project_id, dataset_id, table_id):
  """Creates a BigQuery table with the specified schema."""

  client = bigquery.Client(project=project_id)
  table_ref = client.dataset(dataset_id).table(table_id)

  schema = [
      bigquery.SchemaField('message', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('sender_id', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('receiver_id', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('received_timestamp', 'TIMESTAMP', mode='REQUIRED'),
      bigquery.SchemaField('propagation_time', 'FLOAT', mode='NULLABLE'),
      bigquery.SchemaField('event_type', 'STRING', mode="NULLABLE"),
  ]

  table = bigquery.Table(table_ref, schema=schema)
  table = client.create_table(table)  # API request
  print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

def insert_rows(project_id, dataset_id, table_id, rows_to_insert):
  """Inserts rows into the BigQuery table."""

  client = bigquery.Client(project=project_id)
  table_ref = client.dataset(dataset_id).table(table_id)
  table = client.get_table(table_ref)

  errors = client.insert_rows_json(table, rows_to_insert)
  if errors == []:
      print("New rows have been added.")
  else:
      print(f"Encountered errors while inserting rows: {errors}")

def query_table(project_id, dataset_id, table_id):
  """Queries the BigQuery table and prints the results."""

  client = bigquery.Client(project=project_id)
  query = f"""
      SELECT * 
      FROM `{project_id}.{dataset_id}.{table_id}` 
      LIMIT 10 
  """
  query_job = client.query(query)

  results = query_job.result()

  for row in results:
      print(row)

def update_rows(project_id, dataset_id, table_id):
  """Updates rows in the BigQuery table."""

  client = bigquery.Client(project=project_id)
  query = f"""
      UPDATE `{project_id}.{dataset_id}.{table_id}`
      SET propagation_time = 500  
      WHERE sender_id = 'gossip-statefulset-0' AND receiver_id = 'gossip-statefulset-1'
  """
  query_job = client.query(query)
  query_job.result()
  print("Rows updated successfully.")

if __name__ == '__main__':
  project_id = 'bcgossip-proj'  # Replace with your actual project ID
  dataset_id = 'gossip_simulation'
  table_id = 'gossip_events2'

  # 1. Create the table (uncomment if the table doesn't exist)
  create_table(project_id, dataset_id, table_id)

  # 2. Insert some dummy rows (uncomment to insert data)
  # rows_to_insert = [
  #     {'message': 'Hello from 0', 'sender_id': 'gossip-statefulset-0', 'receiver_id': 'gossip-statefulset-0', 'received_timestamp': time.time_ns(), 'propagation_time': None, 'event_type': 'initiate'},
  #     {'message': 'Hello from 0', 'sender_id': 'gossip-statefulset-0', 'receiver_id': 'gossip-statefulset-1', 'received_timestamp': time.time_ns(), 'propagation_time': 100, 'event_type': 'received'}
  # ]
  # insert_rows(project_id, dataset_id, table_id, rows_to_insert)

  # 3. Query the table
  # query_table(project_id, dataset_id, table_id)

  # 4. Update rows (uncomment to update data)
  # update_rows(project_id, dataset_id, table_id)

  # 5. Query again to see the updated data (uncomment after updating)
  # query_table(project_id, dataset_id, table_id)
