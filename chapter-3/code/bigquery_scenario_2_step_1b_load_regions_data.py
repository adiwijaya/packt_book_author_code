from google.cloud import bigquery

# TODO : Change to your project id
project_id = "packt-data-eng-on-gcp"
public_table_id = "bigquery-public-data.san_francisco_bikeshare.bikeshare_regions"
target_table_id = "{}.raw_bikesharing.regions".format(project_id)

def load_data_from_bigquery_public(public_table_id, target_table_id):
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(destination=target_table_id)

    table = bigquery.Table(target_table_id)
    sql = f"""SELECT * FROM `{public_table_id}`;"""

    query_job = client.query(sql, job_config=job_config)
    query_job.result()

load_data_from_bigquery_public(public_table_id, target_table_id)
