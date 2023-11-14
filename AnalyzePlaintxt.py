# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:28:28 2023

@author: Bumble
"""
import json
import re
import pyodbc
from timeit import default_timer as timer
from RLFunctions.py import Calculate_Rate, Get_Connection



start = timer()
print("start timer works")
f= open(r'..\archive\babbitt.txt',"r",encoding='utf-8')
print("connection established")
lines = f.readlines()
print("lines read")
f.close()
print("closed")
end = timer()
print("time to read gulliver: %f" % (end-start))

start = timer()
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
end = timer()
print("time to populate dictionary: %f" % (end-start))

conn_str = Get_Connection()
cnxn = pyodbc.connect(conn_str);
with cnxn:
    crs = cnxn.cursor()
    crs.execute("drop table RL..Wordstemp;") #I should do this after instead of before, but for the time being
    #I'm still playing around with this in SSMS
    crs.execute("create table RL..Wordstemp (Word VARCHAR(100), Used BIGINT, Rate decimal(15,14));")
    tsql = 'INSERT INTO RL..Wordstemp(Word, Used) VALUES '      
    count = 0 # counter for sql server insert token limit (1000)
    #print('We made it into the insert loop without an error')
    popstart = timer()
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
    print('we didn\'t leave scope, count = %d' % count )
    print('we made it out of the insert loop without an error')
    if len(tsql) > 42:
        tsql = tsql[0:-2]+';'
        crs.execute(tsql) #invalid table name?
Calculate_Rate(conn_str,"RL..Wordstemp")
popend = timer()
print("time to populate temp DB: %f" % (popend-popstart))

