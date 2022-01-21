# NYCCabAssignment
Assignment to find insight in NYC Cab data

Dataset is extracted from (https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)<br>
Only Yellow cab trip details for year 2020 was extracted

## Insights to be identified
* Which DOLocationID is the tip is highest, in proportion to the cost of the ride per quarter 
* Which hour of the day the speed of the taxis is highest (speed = distance/tripduration)

Technology stack
* Azure Databricks to clean and process data from blob to DB
* SQL Server to load the insights
* Azure functions in Python triggered by http to build api to get insights
* Azure Data Factory pipeline for orchestration and data ingestion into blob from source
* Azure Key Vault to store credentials

## ADF Setup

![image](https://user-images.githubusercontent.com/857064/150525731-238ddd93-e29d-4c0c-9c79-f2d49971dc9d.png)

### ADF parameters and variables used
```
Variable : NYCCabMonth=["01","02","03","04","05","06","07","08","09","10","11","12"]
Parameter : NYCCabYear=2020 (Passed during runtime)
```
### Ingestion into BLOB

For each is used to iterate through each month of a given year and extract data from source<br>
The source url is given as dynamic content
```
Base URL: https://s3.amazonaws.com/nyc-tlc/trip+data/
Relative URL: @concat('yellow_tripdata_',dataset().NYCCabYear,'-',dataset().NYCCabMonthLoad,'.csv')
```
Only yellow cab trip details csv is extracted

## Databricks setup
Cluster setup<br>
![image](https://user-images.githubusercontent.com/857064/150527228-e0872891-07e4-4270-935a-5e86fe6f6c9c.png)

### NYCYellowCabIntegration(pyspark)

Make a connection to blob with credentials from key vault and extract data<br>
Cast the dataset columns, filter(as there can be more than input year) based on input from ADF, remove duplicates and convert to parquet file
Load the parquet into blob container

### NYCYellowCabInsight(pyspark)

Read the parquet file and get insights
Connect to Azure SQL server with credentials from key vault and load the insight into a mutable table, meaning the table will be recreated with each load

### Azure Functions(Python)

Building API to extract insights with following endpoints
```
/api/tip/{year}/{quarter}/max (To fetch maximum tip percentage of given quarter)
/api/tip/{year}/max (To fetch maximum tip percentage of all quarter)
/api/speed/{year}/{month}/{date}/max (To fetch maximum speed of cab in any given day by each hour)
```
The python code connects to key vault to get credentials of SQL server and run the below queries for each endpoints
```
SELECT CAST(MAX(MAX_TIP_PERCENTAGE) AS VARCHAR) FROM <TABLE_NAME> WHERE QUARTER=? AND YEAR=?
SELECT CAST(QUARTER AS VARCHAR) AS QUARTER,CAST(MAX(MAX_TIP_PERCENTAGE) AS VARCHAR) AS MAXTIPPERCENTAGES FROM <TABLE_NAME> WHERE YEAR=? GROUP BY QUARTER
SELECT CAST(HOUR_OF_DAY AS VARCHAR) AS HOUR,CONCAT(CAST(MAX_SPEED_IN_DAY AS VARCHAR),'MPH') AS MAXSPEED FROM <TABLE_NAME> WHERE YEAR=? AND MONTH=? AND DATE=?
```
