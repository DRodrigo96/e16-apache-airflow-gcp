

print('IMPORT BIBLIOTECAS')
from pyspark.sql import SparkSession
import sys
print('***------ DONE')

spark = SparkSession.builder.appName('SparkApplicationA').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

print(sys.version)
print('argument-1:', sys.argv[1])
print('argument-2:', sys.argv[2])
print('***------ DONE')

spark.stop()
