import pandas as pd
import os
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/wwiras/mygcp/bcgossip.json'
# Establish BigQuery client
client = bigquery.Client()

# Query BigQuery and fetch results as a DataFrame
sql = """
    SELECT *
    FROM `bcgossip-proj.gossip_simulation.gossip_events`
    LIMIT 10
"""
df = pd.read_gbq(sql, project_id="bcgossip-proj")

# Process and analyze the DataFrame
print(df.head())