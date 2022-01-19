# Databricks notebook source
nyccabinputblob = 'datapipelinestorage1'
nyccabinputblob_key = '6uOgLJ8Xxwv2tQR1xjJvjQ2K78m4CN1i72O/3vDJ1tlLIoKvlNjgfBp1NNo3VjF3RuZmXQ1fP1mm6sASwu/pEg=='
spark.conf.set('fs.azure.account.key.' + nyccabinputblob + '.blob.core.windows.net', nyccabinputblob_key)



# COMMAND ----------

nyccabblobcontainer = 'yellowtaxicabdetails'
filePath = "wasbs://" + nyccabblobcontainer + "@" + nyccabinputblob + ".blob.core.windows.net/yellow_tripdata_2020-01.csv"
#https://datapipelinestorage1.blob.core.windows.net/yellowtaxicabdetails/yellow_tripdata_2020-01.csv
yellowcab = spark.read.format("csv").load(filePath, inferSchema = True, header = True)


# COMMAND ----------

#display(yellowcab)
yellowcab.count()
