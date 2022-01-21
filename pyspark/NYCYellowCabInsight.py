# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Access blob to get the parquet file
nyccabinputblob = 'datapipelinestorage1'
nyccabinputblob_key = dbutils.secrets.get(scope = "NYCCabBlobStorageKey", key = "NYCBlobKey")
spark.conf.set('fs.azure.account.key.' + nyccabinputblob + '.blob.core.windows.net', nyccabinputblob_key)
inputcontainer = 'yellowtaxicabstage'
inputPath = "wasbs://" + inputcontainer + "@" + nyccabinputblob + ".blob.core.windows.net/NYCyellowCab"

yellowcab = spark.read.format("parquet").load(inputPath)

# COMMAND ----------

#get insight of max tip by location in year for per quarter
max_tip_insight=yellowcab.withColumn("tip_percentage",((col("tip_amount")/col("total_amount")*100)).cast(DecimalType(3,2))).groupby('year','quarter','drop_loc').agg(max('tip_percentage').alias("max_tip_percentage"))

#get insight of max speed in a given hour of the day
max_speed_of_taxi=yellowcab.withColumn("hour_of_day",hour(col("pickup_datetime")).cast('int'))\
.withColumn("month",month(col("pickup_datetime")).cast('int'))\
.withColumn("date",date_format(col("pickup_datetime"),'d').cast('int'))\
.withColumn("speed_of_taxi",(col("trip_distance")/col("trip_duration")).cast(DecimalType(4,2)))\
.groupby('year','month','date','hour_of_day').agg(max('speed_of_taxi').alias("max_speed_in_day"))


# COMMAND ----------

#load the value to SQL server db to a mutable table 
username=dbutils.secrets.get(scope = "NYCCabDBAccess", key = "SQLDBAdminUsername")
password=dbutils.secrets.get(scope = "NYCCabDBAccess", key = "SQLDBAdminPassword")
properties={"user": username, "password": password, "driver" : "com.microsoft.sqlserver.jdbc.SQLServerDriver"}
url="jdbc:sqlserver://nyccabdetails.database.windows.net:1433;database=NYCYellowCabInsights"
max_tip_insight.write.jdbc(url=url, table="NYC_YLCAB_MAXTIP", mode="Overwrite", properties=properties)
max_speed_of_taxi.write.jdbc(url=url, table="NYC_TAXI_SPD", mode="Overwrite", properties=properties )
