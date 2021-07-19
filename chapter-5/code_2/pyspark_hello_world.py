#https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/apache_logs/apache_logs
from pyspark.sql import SparkSession
import sys
import random

def calculate_using_python(list):
    sum = 0
    for number in list:
        sum = sum + (number * 10)
    return sum

def main():
    spark = SparkSession.builder \
    .appName('hello_world_spark') \
    .getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("WARN")


    this_is_python_list = [1,2,3,4,5,6,7,8,9,10]
    print("This is stored in single machine python memory:")
    #print(this_is_python_list)

    this_is_spark_rdd = sc.parallelize(this_is_python_list)
    print("This data is distributed into multiple machines as an RDD")
    #print(this_is_spark_rdd.take(10))

    this_is_map = this_is_spark_rdd.map(lambda x: x*10)
    print("This is MAP in MAPREDUCE. This step will multiply by 10 to all inputs in parallel")
    #print(this_is_map.take(10))

    this_is_reduce = this_is_map.reduce(lambda x, y: x + y)
    print("This is REDUCE in MAPREDUCE. This step will add all the numbers")
    print(this_is_reduce)

    sum_number = calculate_using_python(this_is_python_list)
    print("This is another approach using python. Never do this in BigData!")
    print(sum_number)

if __name__ == "__main__":
    main()
