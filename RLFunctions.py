# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:37:37 2023

@author: Bumble
"""
import pyodbc
import json

def Calculate_Rate(conn_str, TBname): 
    """
    Parameters
    ----------
    conn_str : String
        Contains credentials required to connect to SQL server
    TBname : String
        Name of the target table
    Returns
    -------
    None.
    """
    cnxn = pyodbc.connect(conn_str); 
    with cnxn:
        crs = cnxn.cursor()
        crs.execute("""declare @total decimal
                    set @total = (select SUM(Used) from %s)
                    update %s
                    set Rate = Used/@total;""" % (TBname, TBname))
                    
def Get_Connection():
    """
    Returns
    -------
    str
        Contains credentials required to connect to SQL Server
    """
    f=open(r'..\ConnCred.json',"r",encoding='utf-8')
    creds = json.load(f)
    f.close()

    SERVER = creds["SERVER"]
    DATABASE = creds["DATABASE"]
    USERNAME = creds["USERNAME"]
    PASSWORD = creds["PASSWORD"]
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
