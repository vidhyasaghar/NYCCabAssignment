import logging
import azure.functions as func
import pyodbc
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python API to get maximum tip precentage in propotion to ride cost quarter basis')
    year = req.route_params.get('year')
    quarter = req.route_params.get('quarter')
    agg = req.route_params.get('max')
    server = 'nyccabdetails.database.windows.net' 
    database = 'NYCYellowCabInsights' 
    username = os.getenv('SQLDBUsername') 
    password = os.getenv('SQLDBPassword')
    try:
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        cursor.execute("SELECT CAST(MAX(MAX_TIP_PERCENTAGE) AS VARCHAR) FROM NYC_YLCAB_MAXTIP WHERE QUARTER=? AND year=?",quarter,year) 
        row = cursor.fetchone() 
        result=row[0]
        logging.info('The' + str(float(result)) +'is given as response')
    except ValueError:
        return func.HttpResponse("Error in fetching value from server",status_code=500)
    else:
        result_dict={"maxTipPercentage": str(float(result))}
        out_res=json.dumps(result_dict)
        return func.HttpResponse(out_res)
		

