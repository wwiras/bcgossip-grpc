
import pandas_gbq, os

# os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '/Users/wwiras/Documents/src/bcgossip-grpc-proj/bcgossip-proj-685aa1c22491.json'

# Set your project ID (replace 'your-project-id')
project_id = "bcgossip-proj"

# Query BigQuery and fetch results as a DataFrame
sql = """
    SELECT *
    FROM `bcgossip-proj.gossip_simulation.gossip_events`
    LIMIT 10
"""

try:
    df = pandas_gbq.read_gbq(sql, project_id)
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

## Client Big Query method
# import pandas_gbq
# import os
# from google.cloud import bigquery
#
# # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/wwiras/mygcp/bcgossip.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '/Users/wwiras/Documents/src/bcgossip-grpc-proj/bcgossip-proj-685aa1c22491.json'
# # Establish BigQuery client
# client = bigquery.Client()
#
# # Query BigQuery and fetch results as a DataFrame
# sql = """
#     SELECT *
#     FROM `bcgossip-proj.gossip_simulation.gossip_events`
#     LIMIT 10
# """
#
# try:
#     # df = pd.read_gbq(sql, project_id="bcgossip-proj")
#     df = pandas_gbq.read_gbq(sql, project_id="bcgossip-proj")
#     print(df.head())
# except Exception as e:
#     print(f"Error: {e}")