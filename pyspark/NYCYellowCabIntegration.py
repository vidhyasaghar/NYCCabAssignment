# Databricks notebook source
from pyspark.sql.types import *
from pyspark.sql.functions import *
nyccabinputblob = 'datapipelinestorage1'
nyccabinputblob_key = dbutils.secrets.get(scope = "NYCCabBlobStorageKey", key = "NYCBlobKey")
spark.conf.set('fs.azure.account.key.' + nyccabinputblob + '.blob.core.windows.net', nyccabinputblob_key)

# COMMAND ----------

#access blob to get csv file and load parquet file
nyccabblobcontainer = 'yellowtaxicabdetails'
outputContainer = 'yellowtaxicabstage'
dbutils.widgets.text(name = "YearFilter",defaultValue = "2020")
YearFilter = dbutils.widgets.get("YearFilter")
filePath = "wasbs://" + nyccabblobcontainer + "@" + nyccabinputblob + ".blob.core.windows.net/yellow_tripdata_2020-*.csv"
outputPath = "wasbs://" + outputContainer + "@" + nyccabinputblob + ".blob.core.windows.net/"
yellowcab = spark.read.format("csv").load(filePath, inferSchema = True, header = True)

# COMMAND ----------

#cleanup of dataset casting,filter by input year, distinct and write to parquet
df_yellowcab_cleanstep1 = yellowcab.withColumnRenamed("VendorID","vendor_id")\
.withColumn("pickup_datetime",to_timestamp(col("tpep_pickup_datetime")))\
.withColumn("dropoff_datetime",to_timestamp(col("tpep_dropoff_datetime")))\
.withColumn("trip_duration",((unix_timestamp(col("dropoff_datetime"))-unix_timestamp(col("pickup_datetime")))/3600).cast("long"))\
.withColumn("year",year(col("pickup_datetime")).cast('int'))\
.withColumn("quarter",quarter(col("pickup_datetime")).cast('int'))\
.withColumn("passenger_count",col("passenger_count").cast('int'))\
.withColumn("trip_distance",col("trip_distance").cast(DecimalType(3,2)))\
.withColumn("rate_code_id",col("RatecodeID").cast('int'))\
.withColumn("store_and_fwd_flag",col("store_and_fwd_flag").cast('string'))\
.withColumn("pick_up_loc",col("PULocationID").cast('int'))\
.withColumn("drop_loc",col("DOLocationID").cast('int'))\
.withColumn("payment_type",col("payment_type").cast('int'))\
.withColumn("fare_amount",col("fare_amount").cast(DecimalType(23,2)))\
.withColumn("extra",col("extra").cast(DecimalType(23,2)))\
.withColumn("mta_tax",col("mta_tax").cast(DecimalType(23,2)))\
.withColumn("tip_amount",col("tip_amount").cast(DecimalType(23,2)))\
.withColumn("tolls_amount",col("tolls_amount").cast(DecimalType(23,2)))\
.withColumn("improvement_surcharge",col("improvement_surcharge").cast(DecimalType(23,2)))\
.withColumn("congestion_surcharge",col("congestion_surcharge").cast(DecimalType(23,2)))\
.withColumn("total_amount",col("total_amount").cast(DecimalType(23,2)))\
.select(["vendor_id","pickup_datetime","dropoff_datetime","trip_duration","year","quarter","passenger_count","trip_distance","rate_code_id","store_and_fwd_flag","pick_up_loc","drop_loc","payment_type","fare_amount","extra","mta_tax","tip_amount","tolls_amount","improvement_surcharge","congestion_surcharge","total_amount"])
df_yellowcab_cleanstep2=df_yellowcab_cleanstep1.filter(df_yellowcab_cleanstep1.year==YearFilter)
df_yellowcab_cleanstep3=df_yellowcab_cleanstep2.distinct()
df_yellowcab_cleanstep3.write.format("parquet").mode("overwrite").save(outputPath + "NYCyellowCab")
