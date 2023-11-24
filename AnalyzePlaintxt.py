# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:28:28 2023

@author: Bumble
"""
import re
import pyodbc
#from timeit import default_timer as timer
from RLFunctions import Derive_Columns, Get_Connection


filename = input("File name of target in archive: ")
#start = timer()
f= open(r'..\archive\%s.txt'%(filename),"r",encoding='utf-8')
lines = f.readlines()
f.close()
#end = timer()
#print("time to read %s : %f" % (filename,end-start))

#start = timer()
word_counts = {}
# Filters out non-word objects like numbers, dates, URL's, section tags
wordreg = re.compile("(?<=[ \[('{-])[a-zA-Z]+(?=[.!?',_\])} -])")
for i in range(len(lines)):
    matches = re.findall(wordreg,lines.pop())
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
#print("time to populate dictionary: %f" % (end-start))


conn_str = Get_Connection()
cnxn = pyodbc.connect(conn_str);
with cnxn:
    crs = cnxn.cursor()
    # Move drop table statement here to preserve table
    crs.execute("create table RL..Wordstemp (Word VARCHAR(100), Used BIGINT, Rate decimal(15,14),UsedOrder int);")
    tsql = 'INSERT INTO RL..Wordstemp(Word, Used) VALUES '      
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
            tsql = 'INSERT INTO RL..Wordstemp(Word, Used) VALUES '
            count = 0            
    
    #check if there are leftover entries (almost always)    
    if len(tsql) > 42:
        tsql = tsql[0:-2]+';'
        #print(tsql)
        crs.execute(tsql) 
Derive_Columns(conn_str,"RL..Wordstemp")
#popend = timer()
#print("time to populate temp DB: %f" % (popend-popstart))
with cnxn:
    crs = cnxn.cursor()
    crs.execute("""declare @Wordstot decimal
                set @Wordstot=(select COUNT(Word) from RL..Words);
                declare @Wordstemptot decimal
                set @Wordstemptot=(select COUNT(Word) from RL..Wordstemp);
                select SUM(Wordstemp.Rate * ((ATAN(6*(Words.UsedOrder/@Wordstot)-2.5)/2.5+0.48)/(Wordstemp.UsedOrder/@Wordstemptot) ))
                from RL..Wordstemp join RL..Words
                on Wordstemp.word = Words.word;
                """)
    score = crs.fetchall()
    crs.execute("drop table RL..Wordstemp;") 
print("The final rarity score for %s is %f"% (filename,score[0][0]))

          