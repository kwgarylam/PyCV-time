from collections import Counter
from numpy.linalg import norm
from math import log
from keyword import kwlist
import os
import re

def catPythonScript(folder):
  """
  Args:
    folder (String): the target folder

  Returns:
    cat (String): content of all *.py file under the target folder
  """
  cat = ''
  for fn in [folder + '/' + d for d in os.listdir(folder)]:
    content = None
    if os.path.isdir(fn):
      content = catPythonScript(fn)
    if fn.endswith('.py'):
      content = open(fn).read()
    if content:
      cat += content
  return cat

def makeCorpus(root_folder):
  """
  Args:
    root_folder (String): root path of the corpus

  Returns:
    corpus (dict): a dictionary contains term frequency of every experiments
      the key is the experiment's name, the value is a tuple of two lists.
      1st list named 'words' contains all words in the experiments.
      2nd list named 'vector' contains the it-idf vector.
  """
  pattern = re.compile('[\\w\\d]+')
  corpus = {}
  for exp in os.listdir(root_folder):
    path = root_folder + exp 
    if not os.path.isdir(path):
      continue
    content = catPythonScript(path)
    # filter out python keywords and find each words using regex
    words = filter(lambda x: x not in kwlist, re.findall(pattern, content))

    # histogram = { word : how many times the word appears }
    histogram = Counter(words)
    words = histogram.keys()
    values = histogram.values()

    # divided by document length to get term frequency
    sum_ = sum(values)
    vector = map(lambda x: float(x)/sum_, values)
    corpus[exp] = (words, vector)

  # for now, the corpus only has term frequency vectors.
  # calculateTFIDF will turn tf vectors into tf-idf vectors.
  calculateTFIDF(corpus)
  return corpus

def calculateWordIDF(word, corpus):
  """
  Args:
    word (String): the target word to calculate IDF value
    corpus (dict): in order to count how many documents the word appears

  Note:
    in Information Retrieval, a corpus contains several documents.
    in here, a experiment is being treated as a document in IR.

  Returns:
    (float): IDF value of the word under given corpus
  """
  # IDF = log( how many documents the corpus has / (1 + how many documents contain the word) )
  df = 1.0
  for exp in corpus.keys():
    words, _ = corpus[exp]
    if word in words: df += 1
  return log(len(corpus) / df)

def calculateTFIDF(corpus):
  """
  Args:
    corpus (dict): a term frequency corpus
    
  Returns:
    (None): vectors are modified directly in the corpus dictionary
  """
  for exp in corpus.keys():
    words, tfs = corpus[exp]
    for idx, word in enumerate(words):
      idf = calculateWordIDF(word, corpus)
      tfs[idx] *= idf

def expSimilarity(exp1, exp2):
  """ calculate the cosine similarity of 2 experiments """
  words1, vector1 = exp1
  words2, vector2 = exp2

  similarity = 0.0
  for idx1, word in enumerate(words1):
    # if a word is in both exp1 and exp2, similarity increased by tfidf1 * tfidf2
    if word in words2:
      idx2 = words2.index(word)
      similarity += vector1[idx1] * vector2[idx2]
  return similarity

if __name__ == '__main__':
  experiments_folder = '../experiments/'
  corpus = makeCorpus(experiments_folder)

  exps = corpus.keys()
  N = len(corpus)

  for idx, exp in enumerate(exps):
    if idx == N-1:
      break
    # calculate pair similarity
    for next_ in range(idx+1, N):
      n1 = exps[idx]
      n2 = exps[next_]
      similarity = expSimilarity(corpus[n1], corpus[n2])
      # [TODO] should be write into a file such as relation.json in future
      # print to stdout is now for testing only
      print '%0.5f,%s,%s' % (similarity, n1, n2)
