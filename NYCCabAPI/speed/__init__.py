import logging
import pyodbc
import json
import os
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python API to get maximum speed of taxi on a particular day')
    year = req.route_params.get('year')
    month = req.route_params.get('month')
    date = req.route_params.get('date')
    agg = req.route_params.get('max')
    server = 'nyccabdetails.database.windows.net' 
    database = 'NYCYellowCabInsights' 
    username = os.getenv('SQLDBUsername') 
    password = os.getenv('SQLDBPassword')
    try:
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        cursor.execute("SELECT CAST(hour_of_day AS VARCHAR) AS hour,CONCAT(CAST(COALESCE(max_speed_in_day,0) AS VARCHAR),'mph') AS maxSpeed FROM NYC_TAXI_SPD WHERE YEAR=? AND MONTH=? AND DATE=?",year,month,date) 
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        output={"tripSpeeds" : results}
    except:
        return func.HttpResponse("Error in fetching value from server",status_code=500)
    else:
        
        out_res=json.dumps(output)
        return func.HttpResponse(out_res)

