#
# (c) Aravind Natarajan for WorldReader, March 2016.
# Suggest keywords for each book in a folder.
# Works for books in ePub format.
# Adjustable global paraemters are:
#    (i)  'threshold':  This variable decides how many appearances of a word
#     are necessary before the word can be considered as important.
#    (ii) 'numKeyWords': Number of keywords per book.
#    (iii) 'folder': Path where ePub books are located.
#
folder = "books/"  # change this!
numKeywords = 10
threshold = 5
  
import os
import sys
import textract   # needed to read an ePub file

from nltk.corpus  import stopwords
from nltk.stem    import WordNetLemmatizer

# location of the English dictionary.
englishDictionary = "englishDictionary.txt"

# Set of English words.
setofwords = set([val.lower() for val in open(englishDictionary).read().split()])

# Set of stop words.
stops = set([val.lower() for val in stopwords.words('english')])

# Some more stop words that are user defined.
# These are html and/or ePub tags.
extraStops = ["table", "solid", "li", "dashed", "repeat", "choose","span",
"scroll", "screen", "auto", "image", "drawer", "choose", "top", 
"right", "div", "transparent", "none"]

# The lemmatizer.
wnl = WordNetLemmatizer()

def getWords(file):
  # Word count. Given an ePub file, return number of appearances of each word.
  
  text = textract.process(file)
  A = [val for val in text.split("\n")]

  words = {}
  for i in range(0,len(A)):
    B = [val.lower() for val in A[i].split(" ") if val.lower() in setofwords and val.lower() not in stops and val.lower() not in extraStops]
    if B <> []:
      for word in B:
        w = wnl.lemmatize(word)
        if w not in words: words[w] = 1
        else: words[w] += 1

  return words
  
def suggest(wordsInBooks,myBook):
  # Suggest some keywords using Bayes' theorem.
  
  numBooks = len(wordsInBooks)
  pMyBook = 1./numBooks
  pOtherBook = (numBooks-1.)/numBooks
    
  numWordsInMyBook = 0; numWordsInOtherBooks = 0
  wordsInMyBook = wordsInBooks[myBook]
  for word in wordsInMyBook: numWordsInMyBook += wordsInMyBook[word]
      
  wordsInOtherBooks = {}
  for word in wordsInMyBook: wordsInOtherBooks[word] = 0
  for book in wordsInBooks:
    if book <> myBook:
      words = wordsInBooks[book]      
      for word in words:
        numWordsInOtherBooks += words[word]
        if word in wordsInOtherBooks:
          wordsInOtherBooks[word] += words[word]
      
  bayes = {}
  for word in wordsInMyBook:
    pWordInMyBook = 1.*wordsInMyBook[word]/numWordsInMyBook
    pWordInOtherBooks = 1.*wordsInOtherBooks[word]/numWordsInOtherBooks        
    bayes[word] = (pWordInMyBook*pMyBook) / ((pWordInMyBook*pMyBook) + (pWordInOtherBooks*pOtherBook))
     
  myKeywords = []
  ctr = 0          
  keywords = sorted(bayes, reverse=True, key=bayes.__getitem__)
  for keyword in keywords:  
    if wordsInMyBook[keyword] > threshold:
      myKeywords.append(keyword)
      if ctr > numKeywords: break
      ctr += 1    

  return myKeywords          
  
def main():  

  # collect all books in the folder.
  books = [val for val in os.listdir(folder) if val[0] <> "."]  

  # Read all books. Count number of words in each book.  
  wordsInBooks = {}
  for book in books:
    print "Reading %s "%book
    words = getWords(folder+book)  
    wordsInBooks[book] = words
  print "\n"  

  # Suggest keywords for each book.
  for myBook in books:
    print myBook    
    keywords = suggest(wordsInBooks,myBook)
    print keywords
    print "\n"   

if __name__ == "__main__":
  main()
  