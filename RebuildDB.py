# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:58:34 2023

@author: Bumble
"""
import json
import re
import pyodbc
from RLFunctions.py import Calculate_Rate, Get_Connection
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
    for word in word_counts.keys():
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
    #print(end - start) # as of 11/2, the python section takes 3.5~4 seconds
    #start = timer()
    with cnxn:
        crs = cnxn.cursor()
        crs.execute("create table #Wordstemp (Word VARCHAR(100), Used BIGINT)")
        tsql = 'INSERT INTO #Wordstemp(Word, Used) VALUES '      
        count = 0 # counter for sql server insert token limit (1000)
        #print('We made it into the insert loop without an error')
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
        #print('we made it out of the insert loop without an error')
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
            
        #From here, run the tsql command that merges the elements in wordstemp with words
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
    #print(end-start) # As of 11/1, the sql section takes ~8s on large files
    
    #Exiting scope of connection closes it and commits changes
    
conn_str = Get_Connection()
for i in range(1,606):
    filepath = r'..\archive\enwiki20201020\articles_'+str(i)+'.json'
    Add_To_Words(conn_str,filepath)
Calculate_Rate(conn_str, "RL..Words")


