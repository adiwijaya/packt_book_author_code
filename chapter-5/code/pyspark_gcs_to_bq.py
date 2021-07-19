#https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/apache_logs/apache_logs
from pyspark.sql import SparkSession
import sys

BUCKET="aw-general-dev"
OUTPUT_TABLE="sandbox_us.spark_log"
GCS_TEMP="aw-general-dev/tmp"


def main():
    spark = SparkSession.builder \
    .appName('spark_hdfs_to_hdfs') \
    .getOrCreate()

    sc = spark.sparkContext
    sc.setLogLevel("WARN")
    log4jLogger = sc._jvm.org.apache.log4j
    log = log4jLogger.LogManager.getLogger(__name__)

    a = sc.textFile('gs://{}/dummy_data/logs_example.txt'.format(BUCKET))
    print(" ### The original file ### ")
    print(a.take(3))

    b = a.map(lambda x: x.split(" "))
    print(" ### The logs parsed using space delimiter ### ")
    print(b.take(3))

    ### RDD approach
    ip = b.map(lambda x: (x[0],1))
    reduce_by_key = ip.reduceByKey(lambda x,y: x+y)
    top_ip = reduce_by_key.sortBy(lambda a: -a[1])
    print(" ### Top 5 most active IP using RDD approach ### ")
    print(top_ip.take(5))

    c = b.map(lambda x: (x[0], x[3], x[5], x[6]))
    columns = ["ip","date","method","url"]
    df = c.toDF(columns)
    df.createOrReplaceTempView('df')

    sql = f"""
      SELECT
      ip,
      to_timestamp(cast(substring(date,2, length(date)) as string),'dd/MMM/yyyy:hh:mm:ss') as `TIMESTAMP_DATE`,
      regexp_replace(method,"[^A-Z]","") as method,
      CASE WHEN url LIKE '%/articles/%' THEN 'articles'
      WHEN url LIKE '%/blog/%' THEN 'blog'
      ELSE NULL
      END AS url_type,
      url
      FROM df
      WHERE url LIKE '%/article%' OR (url LIKE '%/blog/%' AND url NOT LIKE '%/blog/tags%')
      """

    clean_df = spark.sql(sql)
    print(" ### Get only articles and blogs records ### ")
    clean_df.show(5, False)
    clean_df.createOrReplaceTempView('clean_df')

    # Load to BigQuery Table
    log.info("Loading to BigQuery")
    clean_df.write.format('bigquery') \
        .option('table', 'sandbox_us.clean_df') \
        .mode('overwrite') \
        .option("temporaryGcsBucket", GCS_TEMP) \
        .save()

    ### SparkSQL approach
    sql = f"""
      SELECT
      url, count(*) as cnt
      FROM clean_df
      GROUP BY url
      ORDER BY cnt DESC
      LIMIT 5
      """
    result = spark.sql(sql)
    print(" ### Top 5 most popular article / blogs url using SparkSQL ### ")
    result.show(5, False)

    # Load to BigQuery Table
    log.info("Loading to BigQuery")
    result.write.format('bigquery') \
        .option('table', OUTPUT_TABLE) \
        .mode('overwrite') \
        .option("temporaryGcsBucket", GCS_TEMP) \
        .save()
    spark.stop()
    log.info("The query result stored in BigQuery table : {}".format(OUTPUT_TABLE))


if __name__ == "__main__":
    main()
