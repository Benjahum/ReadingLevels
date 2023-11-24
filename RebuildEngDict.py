# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 13:54:11 2023

@author: Bumble
"""

import json
import pyodbc
from RLFunctions.py import Get_Connection



f = open(r'..\archive\words_dictionary.json',"r",encoding='utf-8')
words = json.load(f)
f.close()

conn_str = Get_Connection()
cnxn = pyodbc.connect(conn_str);
with cnxn:
    crs = cnxn.cursor()
    crs.execute("""IF EXISTS (Select * from INFORMATION_SCHEMA.TABLES
			    WHERE Table_Name = 'Eng_Dict')
                DROP TABLE RL..Eng_Dict;""")
    crs.execute('CREATE TABLE RL..Eng_Dict(Word VARCHAR(100));')
    tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
    count = 0
    for word in words:
        if count < 997:
            tsql += "(\'" + word + "\'), "
            count += 1
        else:
            tsql += "(\'" + word + "\');"
            crs.execute(tsql)
            tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
            count = 0
            
    if len(tsql) > 38:
        crs.execute(tsql[0:-2]+';')

    #Exiting the scope of connection commits and closes
        
    