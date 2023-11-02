# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 13:54:11 2023

@author: Bumble
"""

import json
import pyodbc

f=open(r'..\ConnCred.json',"r",encoding='utf-8')
creds = json.load(f)
f.close()

SERVER = creds["SERVER"]
DATABASE = creds["DATABASE"]
USERNAME = creds["USERNAME"]
PASSWORD = creds["PASSWORD"]
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'


f = open(r'..\archive\words_dictionary.json',"r",encoding='utf-8')
words = json.load(f)
f.close()


cnxn = pyodbc.connect(conn_str);
with cnxn:
    crs = cnxn.cursor()
    crs.execute('DROP TABLE RL..Eng_Dict;')
    crs.execute('CREATE TABLE RL..Eng_Dict(Word VARCHAR(100));')
    
    tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
    count = 0
    #print('We made it into the insert loop without an error')
    for word in words:
        if count < 997:
            tsql += "(\'" + word + "\'), "
            count += 1
        else:
            tsql += "(\'" + word + "\');"
            #print(tsql)
            crs.execute(tsql)
            tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
            count = 0
            
    #check if there are leftover entries (almost always)
    #print('we made it out of the insert loop without an error')
    if len(tsql) > 38:
        crs.execute(tsql[0:-2]+';')

    #Exiting the scope of connection commits and closes
        
    