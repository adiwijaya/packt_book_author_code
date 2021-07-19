#https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/apache_logs/apache_logs
from pyspark.sql import SparkSession

CLUSTER_NAME="cluster-b708-m"

spark = SparkSession.builder \
.appName('spark_hdfs_to_hdfs') \
.getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")

log_files_rdd = sc.textFile('hdfs://{}/user/admin/data/logs_example/*'.format(CLUSTER_NAME))
print(" ### The original file ### ")
print(a.take(3))

splitted_rdd = log_files_rdd.map(lambda x: x.split(" "))
print(" ### The logs parsed using space delimiter ### ")
print(splitted_rdd.take(3))

### RDD approach
# ip = b.map(lambda x: (x[0],1))
# reduce_by_key = ip.reduceByKey(lambda x,y: x+y)
# top_ip = reduce_by_key.sortBy(lambda a: -a[1])
# print(" ### Top 5 most active IP using RDD approach ### ")
# print(top_ip.take(5))

selected_col_rdd = splitted_rdd.map(lambda x: (x[0], x[3], x[5], x[6]))
columns = ["ip","date","method","url"]
logs_df = selected_col_rdd.toDF(columns)
logs_df.createOrReplaceTempView('logs_df')

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
  FROM logs_df
  WHERE url LIKE '%/article%' OR (url LIKE '%/blog/%' AND url NOT LIKE '%/blog/tags%')
  """

clean_df = spark.sql(sql)
print(" ### Get only articles and blogs records ### ")
clean_df.show(5, False)
#clean_df.createOrReplaceTempView('clean_df')
clean_df.write.save('hdfs://{}/user/admin/data/clean_df'.format(CLUSTER_NAME), format='csv', mode='overwrite')

### SparkSQL approach
# sql = f"""
#   SELECT
#   url, count(*) as cnt
#   FROM clean_df
#   GROUP BY url
#   ORDER BY cnt DESC
#   LIMIT 5
#   """
# result = spark.sql(sql)
# print(" ### Top 5 most popular article / blogs url using SparkSQL ### ")
# result.show(5, False)
# result.write.save('hdfs://{}/user/admin/data/result_log_counts'.format(CLUSTER_NAME), format='csv', mode='overwrite')
