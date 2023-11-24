# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:58:34 2023

@author: Bumble
"""
import json
import re
import pyodbc
from RLFunctions import Derive_Columns, Get_Connection
#from timeit import default_timer as timer

def Filter_Eng(crs):
    """
    Parameters
    ----------
    crs : Cursor Object
        Allows this function to act on the database
    Returns
    -------
    None.

    """
    # The English Dict is a pre-existing table
    # Created with RebuildEngDict.py
    tsql ="""DELETE FROM #Wordstemp
            WHERE NOT EXISTS (
            SELECT Word FROM RL..Eng_Dict
            WHERE Eng_Dict.Word = #Wordstemp.Word
            ); """
    crs.execute(tsql)

def Add_To_Words(conn_str, filepath):
    '''
    Parameters
    ----------
    conn_str : String
        Contains the string required to log in to the database
    filepath : String
        The path to a json file containing the text from multiple wikipedia articles
    Returns
    -------
    None.

    '''
    
    
    #start = timer()     
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
    remove_these = set() #Convert all to lowercase, consolidate duplicates, remove junk
    for word in words:
        if len(word) > 35: #The longest word in the current filter dictionary is 31 letters
            remove_these.add(word)
            continue
        lc = word.lower()
        if lc != word and lc in words:
            word_counts[lc] += word_counts[word]
            remove_these.add(word)
    for word in remove_these:
        del word_counts[word]
    
    #end = timer()
    #print("PythonTotal")
    #print(end - start) 
    #start = timer()
    with cnxn:
        crs = cnxn.cursor()
        crs.execute("""IF EXISTS (Select * from INFORMATION_SCHEMA.TABLES
    			    WHERE Table_Name = 'Words')
                    DROP TABLE RL..Eng_Dict;""")
        crs.execute("create table RL..Words (Word varchar(100), Used bigint, Rate decimal(15,14), UsedOrder int);")
        crs.execute("create table #Wordstemp (Word VARCHAR(100), Used BIGINT);")
        tsql = 'INSERT INTO #Wordstemp(Word, Used) VALUES '      
        count = 0 # counter for sql server insert token limit (1000)
        #popstart = timer()
        for word, used in word_counts.items():
            if count < 998:
                tsql += '(\'' + word + '\',' + str(used) + '), '
                count += 1
            else:
                tsql += "(\'"+word+'\','+ str(used) + ");"
                #print(tsql)
                crs.execute(tsql)
                tsql = 'INSERT INTO #Wordstemp(Word, Used) VALUES '
                count = 0
                
        #check if there are leftover entries (almost always)
        if len(tsql) > 41:
            crs.execute(tsql[0:-2]+';')
        #popend= timer()
        #print("The add loop")
        #print(popend-popstart) # The loop burns something like 7-8s on the larger files
        #filtstart = timer()
        Filter_Eng(crs)
        #filtend = timer()
        #print("English filter")
        #print(filtend - filtstart) # Filter is fast 
            
        # merges the elements in wordstemp with words
        #mergestart = timer()
        tsql = """UPDATE RL..Words
                SET Words.Used = Words.Used + #Wordstemp.Used
                FROM #Wordstemp 
                WHERE Words.Word = #Wordstemp.Word;"""
        crs.execute(tsql) # Updates values for known words
        
        #mergeend = timer()
        #print("Merging contained words")
        #print(mergeend-mergestart)
        #missstart= timer()
        tsql ="""INSERT INTO RL..Words (Word, Used)
                SELECT * FROM #Wordstemp AS Wt
                WHERE NOT EXISTS (
                SELECT Word FROM RL..Words AS W 
                WHERE W.Word = Wt.Word); """ 
        crs.execute(tsql) #Adds new words
        
        #missend = timer()
        #print("insert missing")
        #print(missend-missstart)
        
        #trunstart = timer()
        crs.execute('DROP TABLE #WORDSTEMP;')
        #trunend = timer()
        #print("truncate")
        #print(trunend-trunstart)
        
        
    #end = timer()
    #print(end-start)
    
    #Exiting scope of connection closes it and commits changes
    
conn_str = Get_Connection()
for i in range(1,606):
    filepath = r'..\archive\enwiki20201020\articles_'+str(i)+'.json'
    Add_To_Words(conn_str,filepath)
Derive_Columns(conn_str, "RL..Words")


