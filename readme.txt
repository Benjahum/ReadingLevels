Just going to put a text file in for now, to remind myself how it works.
What is it that I need to do?

I need to be able to read in large amounts of text and pair each word with its frequency in the data set.
I need an initial array based on the training data to compare those of new batches of text against.
I need to do the actual comparison, and reduce the output to a number. 
This number should include in its calculation consideration for the rarity relative to the training set, the variety, and the frequency of the words in the test set.
I should entertain the possibility of changing the way this number is calculated.

How am I going to do it?
I can't do anything until I produce the array based on the training data, so the first main task is
Create a prototype that handles the problem for small batches of text, test it
  Read, count words, calculate frequencies, sort
Scale up to the size of the training data
  If one file can be processed at a time, create a driver that sequentially processes data, then writes the results to a collective between switching data files.
  This is several separate jobs, the driver, and the handling of the total data, neither of which relies on the initial file processor
Once I have the training data, I should be able to use the same initial processor on new test data
  There may be complications here- my training data arrived in JSON form. I can either convert test data to JSON or make a new processor
Then I need to handle the comparison of the training and the test data

Once I have the ability to produce numbers from test data, I can consider attempting to roughly match the output to other existing strategies
That is, use as test data text that other similar processes have already ranked and make sure my product correctly determines which things are harder to read.
Something like gutenberg.org should help with this, a library of presumeably public domain ebooks
the lexile wikipedia article led me here, https://cdn.lexile.com/m/cms_page_media/135/Lexile%20Map_8.5x11_FINAL_Updated_May_2013%20(4).pdf
a list of books by lexile reading level. Things like government documents should be easily accessible and I believe a number of these books will be on gutenberg.

