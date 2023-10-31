# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:58:34 2023

@author: Bumble
"""
import json
import re
import pyodbc

#Establish connection to local MS SQL Server with generic credentials
SERVER = 'localhost'
DATABASE = 'RL'
USERNAME = 'everyone'
PASSWORD = 'MoreSecure4$'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
cnxn = pyodbc.connect(conn_str);



f = open(r"RawData\articles_001.json","r",encoding='utf-8')
articles = json.load(f)
f.close()


word_counts = {}
# Filters out non-word objects like numbers, dates, URL's, section tags
wordreg = re.compile("(?<=[ \[('{-])[a-zA-Z]+(?=[.!?',_\])} -])")
for i in range(len(articles)):
    matches = re.findall(wordreg,articles.pop()["text"])
    #populates the dictionary
    for word in matches:
        if word_counts.get(word) is not None:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
            
            
words = word_counts.keys()
remove_these = set() #Convert all to lowercase, consolidate duplicates
for word in word_counts.keys():
    lc = word.lower()
    if lc != word and lc in words:
        word_counts[lc] += word_counts[word]
        remove_these.add(word)
for word in remove_these:
    word_counts.pop(word)

with cnxn:
    crs = cnxn.cursor()
    #instantiate add string
    tsql = 'INSERT INTO RL..Wordstemp(Word, Used) VALUES '
    #instantiate counter
    count = 0
    #loop over word counts, probably items because i need word and used
    #print('We made it into the insert loop without an error')
    for word, used in word_counts.items():
        #check if we're about to overflow multi-add limit
        if count < 997:
            #throw the word onto the pile
            tsql += '(\'' + word + '\',' + str(used) + '), '
            #increment the counter
            count += 1
        #else
        else:
            #if we are, throw the last word on 
            tsql += "(\'"+word+'\','+ str(used) + ");"
            #add to the DB
            #print(tsql)
            crs.execute(tsql)
            #reset the add string
            tsql = 'INSERT INTO RL..Wordstemp(Word, Used) VALUES '
            #reset the counter
            count = 0
            
    #check if there are leftover entries
    #print('we made it out of the insert loop without an error')
    if len(tsql) > 41:
        crs.execute(tsql[0:-2]+';')
        #add it to the database
        
    #From here, run the tsql command that merges the elements in wordstemp with words
    tsql = """UPDATE RL..Words
            SET Words.Used = Words.Used + Wordstemp.Used
            FROM RL..Wordstemp 
            WHERE Words.Word = Wordstemp.Word;"""
    crs.execute(tsql)
    #Then add in the uniquely appearing words
    tsql ="""INSERT INTO RL..Words (Word, Used)
            SELECT * FROM RL..Wordstemp AS Wt
            WHERE NOT EXISTS (
            SELECT Word FROM RL..Words AS W 
            WHERE W.Word = Wt.Word); """
    crs.execute(tsql)
    crs.execute('TRUNCATE TABLE RL..WORDSTEMP;')
    
        
#Exiting scope of connection closes it and commits changes
    
        

#Alright, I accidentally nuked all of my previous progress
#At the end of things, I had a file that was capable of building the whole database
#So the major pieces missing from this, are the localhost access information for the server that goes at the top
#the loop that handles adding words 998 at a time (you can do 1000 consecutive adds in one before you need bulk add)
#and the loop that generates file access to cover the entire set
#remember after each file to close the connection


