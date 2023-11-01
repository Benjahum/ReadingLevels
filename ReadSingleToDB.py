# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:58:34 2023

@author: Bumble
"""
import json
import re
import pyodbc
from timeit import default_timer as timer

#Establish connection to local MS SQL Server with generic credentials



def Filter_Eng(crs):
    #I'm just going to have another file to rebooting the english dictionary
    #Okay, the file for rebuilding the english dictionary is done- we just assume its sitting there
    #We've passed the cursor, and we want to remove from wordstemp anything that isn't in Eng_Dict
    #real questions- is it better to do this with each file or once at the end?
    #Its probably fine, the python is the slow bit anyway
    tsql ="""DELETE FROM RL..Wordstemp
            WHERE NOT EXISTS (
            SELECT Word FROM RL..Eng_Dict
            WHERE Eng_Dict.Word = Wordstemp.Word
            ); """
    crs.execute(tsql)

def Add_To_Words(conn_str, filepath):
    start = timer()     
    cnxn = pyodbc.connect(conn_str);
    
    
    
    f = open(filepath,"r",encoding='utf-8')
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
        if len(word) > 35:
            remove_these.add(word)
            continue
        #I checked the dictionary i'm filtering with, the longest word in it is 31 letters
        lc = word.lower()
        if lc != word and lc in words:
            word_counts[lc] += word_counts[word]
            remove_these.add(word)
    for word in remove_these:
        word_counts.pop(word)
    
    end = timer()
    print(end - start) # as of 11/1, the python section takes ~4 seconds
    start = timer()
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
            
        Filter_Eng(crs)
            
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
        
        
    end = timer()
    print(end-start) # As of 11/1, the sql section takes ~1.3s
    #Exiting scope of connection closes it and commits changes
    
    
SERVER = 'localhost'
DATABASE = 'RL'
USERNAME = 'everyone'
PASSWORD = 'MoreSecure4$'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

for i in range(1,606):
    filepath = r'..\archive\enwiki20201020\articles_'+str(i)+'.json'
    Add_To_Words(conn_str,filepath)

#It's... Not hard to put this in a loop, actually.

#Alright, I accidentally nuked all of my previous progress
#At the end of things, I had a file that was capable of building the whole database
#So the major pieces missing from this, are the localhost access information for the server that goes at the top
#the loop that handles adding words 998 at a time (you can do 1000 consecutive adds in one before you need bulk add)
#and the loop that generates file access to cover the entire set
#remember after each file to close the connection


