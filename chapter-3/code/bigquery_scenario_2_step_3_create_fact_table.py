from google.cloud import bigquery

# TODO : Change to your project id
project_id = "packt-data-eng-on-gcp"
target_table_id = "{}.dwh_bikesharing.fact_trips_daily".format(project_id)

def create_fact_table(target_table_id):
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(destination=target_table_id)

    table = bigquery.Table(target_table_id)
    sql = f"""SELECT DATE(start_date) as date,
          start_station_id,
          region_id,
          COUNT(trip_id) as total_trips,
          SUM(duration_sec) as sum_duration_sec,
          AVG(duration_sec) as avg_duration_sec
          FROM `{project_id}.raw_bikesharing.trips`
          JOIN `{project_id}.raw_bikesharing.stations`
          ON trips.start_station_id = stations.station_id
          GROUP BY date, start_station_id, region_id
          ;"""

    query_job = client.query(sql, job_config=job_config)
    query_job.result()

create_fact_table(target_table_id)
