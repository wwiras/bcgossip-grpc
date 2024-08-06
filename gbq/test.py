import pandas as pd
from google.cloud import bigquery

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
