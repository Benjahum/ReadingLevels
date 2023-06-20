# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 13:58:34 2023

@author: Bumble
"""
import json
import re


f = open(r"RawData\articles_001.json","r",encoding='utf-8')
# without the encoding, text parsing fails
articles = json.load(f)
f.close()
# articles is now a list which contains dictionaries
# for each article in articles, the options are "id", "text", and "title"

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
remove_these = set()
# The regex is not case sensitive: consolidate words that are not proper nouns
# This will, unfortunately, consume some peoples names (eg Carpenter)
# but this should have a greater effect on the capitalization from the
# beginning of sentences.
for word in word_counts.keys():
    lc = word.lower()
    if lc != word and lc in words:
        word_counts[lc] += word_counts[word]
        remove_these.add(word)
for word in remove_these:
    word_counts.pop(word)

f = open(r"Data\ProtoOut.json","w")
json.dump(word_counts,f,indent=0)
#indent key is required for the text to not be written all on one line.


