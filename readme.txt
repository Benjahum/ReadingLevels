What is it?


ReadingLevels is mostly a practice exercise for me in using Python and SQL. 

When I was going through the American public school system, administration was concerned about evaluating how well the children were reading. 
Part of that included making sure the kids were reading age appropriate works, not in terms of content but in terms of complexity. 
There are multiple companies that provide a service giving scores to written works to give indicators about what kids should read at different ages. 
Unfortunately, they don't explain how it works or offer the public a way to score arbitrary text.
I wanted to see if I could build something like that myself.

This code collectively takes a dump of wikipedia articles, 
filters the contents down to words, 
filters according to the contents of an english dictionary, 
stores that in a database in MS SQL Server to be used in comparison with the text of input files,
and finally prints a score to the console.


How do I get it to work?


It uses MS SQL Server, a dataset of wikipedia articles, and an english dictionary.

Get MS SQL Server and SQL Server Management Studio (SSMS)

https://www.microsoft.com/en-us/sql-server/sql-server-downloads
https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16

Get the dump of wikipedia articles I used, already formatted as json
https://www.kaggle.com/datasets/ltcmdrdata/plain-text-wikipedia-202011

Get the english dictionary I used, already formatted as json
https://github.com/dwyl/english-words

As of now, the code expects the folder
archive\enwiki20201020
to exist in the same directory as the top level ReadingLevels folder.
The files that comprise the dataset should be inside, renamed to
articles_1 ... articles_10 ... articles_606

The json file containing the dictionary should be stored in archive,
along with the plaintext files of anything you want analyzed by the program.

The code expects a json file of this form to exist in the same directory as the top level ReadingLevels folder
ConnCred.json
{
	"SERVER":"",
	"DATABASE":"RL",
	"USERNAME":"",
	"PASSWORD":""
}
You will need to configure SQL Server such that there exists a database named RL and this file contains credentials to an ID with the permissions to manipulate the database.

One you can connect to SQL Server,run RebuildEngDict. This should populate the dictionary table in SQL Server.
If it worked, run RebuildDB.
This can take around two hours, depending on hardware. 
The bulk of the time is spent just loading the words into the table. 
Be sure you have the time to complete the run, because the first thing it will do is delete the old table if it exists.

Once the database is loaded in, you can run AnalyzePlaintxt.
It will prompt you for the name of a txt file (do not include .txt), then it will return a number.


What is it actually doing? or What do the numbers mean?


The actual calculation is a weighted sum of the rates at which each word in the text were used.
The sum of the rates should add up to one (up to floating point errors), and the weights are a function of the relative rarity in the reference database and the rarity in the analyzed text.
Basically, if the chosen word is common in the reference database but uncommon in the analyzed text, or if it is relatively rare in the database but common in the text, the contribution will be larger.

If this program were run on the database with its own weights applied, it should return one.

So in short, if the number is less than one, you should expect the text to be relatively easy to understand compared to the text of an average wikipedia article, because it uses mostly common words.
If the number is much greater than one, it should be harder to read because it uses more words that are less common.

Please note that this result will be biased. Many wikipedia articles cover topics in science.
I used this program to analyze Gulliver's Travels and Flatland.
Gulliver's Travels yielded ~3.6
and Flatland ~2.12

You can access these and many other books free via the Gutenberg Project
https://www.gutenberg.org/

Gulliver's travels is an adventure story and Flatland asks the reader to imagine the world in two dimensions.
I said the database should return one if it analyzed itself, so the implication is that the more similar your text is to the average wikipedia article from the given dataset, the closer the score should be to one.
Something like slang terms might get a high score because they are used rarely in the data.

If one were so inclined, they could generate a different database by reading in more, fewer, or select articles
or just reading in any other text by formatting it in json.

If you want to get an itemized list of score contributions by words, this is the query I used after arranging AnalyzePlaintxt to not drop the table after the run.

declare @Wordstot decimal
set @Wordstot=(select COUNT(Word) from RL..Words);
declare @Wordstemptot decimal
set @Wordstemptot=(select COUNT(Word) from RL..Wordstemp);
select Wordstemp.Word, Wordstemp.Used, Wordstemp.Rate as Domain, (ATAN(6*(Words.UsedOrder/@Wordstot)-2.5)/2.5+0.48) as NMLWords, 
Wordstemp.UsedOrder/@Wordstemptot as NMLWordstemp,((ATAN(6*(Words.UsedOrder/@Wordstot)-2.5)/2.5+0.48)/(Wordstemp.UsedOrder/@Wordstemptot) ) as weights,
Wordstemp.Rate * ((ATAN(6*(Words.UsedOrder/@Wordstot)-2.5)/2.5+0.48)/(Wordstemp.UsedOrder/@Wordstemptot) ) as products
from RL..Wordstemp join RL..Words
on Wordstemp.word = Words.word
order by products desc;
select SUM(Wordstemp.Rate * ((ATAN(6*(Words.UsedOrder/@Wordstot)-2.5)/2.5+0.48)/(Wordstemp.UsedOrder/@Wordstemptot) ))
from RL..Wordstemp join RL..Words
on Wordstemp.word = Words.word;
 


What happens if you feed this file into it?
This text returns a score of: ~0.19