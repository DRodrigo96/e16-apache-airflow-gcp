

print('IMPORT BIBLIOTECAS')
from pyspark.sql import SparkSession
import json
import sys
print('***------ DONE')


print('***------ SPARK SESSION... ------***')
spark = SparkSession.builder.appName('SparkApplicationB').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')
print('***------ DONE')


print('***------ SETTING VARIABLES... ------***')
GCS_URI_INPUT = 'gs://{}/pyspark/data/retail_2021.csv'.format(sys.argv[1])
GCS_URI_OUTPUT = 'gs://{}/pyspark/pyspark-output/{}/retail_2021_output.csv'.format(sys.argv[1], sys.argv[2])

print('input: {}'.format(GCS_URI_INPUT))
print('output: {}'.format(GCS_URI_OUTPUT))
print('***------ DONE')


print('***------ LECTURA DESDE GCS... ------***')
retail_df = (
    spark
    .read
    .option('header', 'true')
    .option('inferSchema', value=True)
    .option('delimiter', ';')
    .csv('{}'.format(GCS_URI_INPUT))
)
print('***------ DONE')


print('***------ SCHEMA ------***')
print(json.dumps(json.loads(retail_df._jdf.schema().json()), indent=4, sort_keys=True))
print('***------ DONE')


print('***------ COLUMNAS SELECCIONADAS ------***')
retail_df.select('quant', 'uprice_usd', 'total_inc').show(15)
print('***------ DONE')


print('***------ SPARK SQL TRANSFORMATION... ------***')
retail_df.createOrReplaceTempView('retail_years')
avg_variables = spark.sql(
    '''
    SELECT year, area, AVG(quant) AS avg_quant, AVG(uprice_usd) AS avg_uprice_usd, AVG(total_inc) AS avg_total_inc 
    FROM retail_years GROUP BY year, area
    '''
)
print('***------ DONE')


print('***------ COLUMNAS AGRUPADAS ------***')
avg_variables.show(15)
print('***------ DONE')


print('***------ GUARDADO EN GCS... ------***')
(
    avg_variables
    .write
    .option('header', True)
    .mode('overwrite')
    .csv('{}'.format(GCS_URI_OUTPUT))
)
print('***------ DONE')

spark.stop()
