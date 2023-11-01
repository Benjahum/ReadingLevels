# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 13:54:11 2023

@author: Bumble
"""

import json
import pyodbc

SERVER = 'localhost'
DATABASE = 'RL'
USERNAME = 'everyone'
PASSWORD = 'MoreSecure4$'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'


f = open(r'..\archive\words_dictionary.json',"r",encoding='utf-8')
words = json.load(f)
f.close()

#alright, i can just iterate over words, the first thing itll grab is the string that represents the word


cnxn = pyodbc.connect(conn_str);
with cnxn:
    crs = cnxn.cursor()
    crs.execute('DROP TABLE RL..Eng_Dict;')
    crs.execute('CREATE TABLE RL..Eng_Dict(Word VARCHAR(100));')
    
    tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
    #instantiate counter
    count = 0
    #loop over word counts, probably items because i need word and used
    #print('We made it into the insert loop without an error')
    for word in words:
        #check if we're about to overflow multi-add limit
        if count < 997:
            #throw the word onto the pile
            tsql += "(\'" + word + "\'), "
            #increment the counter
            count += 1
        #else
        else:
            #if we are, throw the last word on 
            tsql += "(\'" + word + "\');"
            #add to the DB
            #print(tsql)
            crs.execute(tsql)
            #reset the add string
            tsql = 'INSERT INTO RL..Eng_Dict(Word) VALUES '
            #reset the counter
            count = 0
            
    #check if there are leftover entries
    #print('we made it out of the insert loop without an error')
    if len(tsql) > 38:
        crs.execute(tsql[0:-2]+';')
        #add it to the database
        
    