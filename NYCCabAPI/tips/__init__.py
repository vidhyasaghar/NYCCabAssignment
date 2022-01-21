import logging
import azure.functions as func
import pyodbc
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python API to get maximum tip precentage in propotion to ride cost for all quarters')
    year = req.route_params.get('year')
    agg = req.route_params.get('max')
    server = 'nyccabdetails.database.windows.net' 
    database = 'NYCYellowCabInsights' 
    username = os.getenv('SQLDBUsername') 
    password = os.getenv('SQLDBPassword')
    try:
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        cursor.execute("SELECT CAST(QUARTER AS VARCHAR) AS quarter,CAST(MAX(MAX_TIP_PERCENTAGE) AS VARCHAR) AS maxTipPercentages FROM NYC_YLCAB_MAXTIP WHERE year=? GROUP BY QUARTER",year)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        output={"maxTipPercentages" : results}
    except ValueError:
        return func.HttpResponse("Error in fetching value from server",status_code=500)
    else:
        out_res=json.dumps(output)
        return func.HttpResponse(out_res)