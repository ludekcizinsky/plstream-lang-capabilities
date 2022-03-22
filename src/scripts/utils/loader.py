# loader.py
import os
import sys
import gzip
import json
import math
import numpy as np
from scipy.sparse import load_npz

# globals
DATA = {
    'raw': 'data/raw',
    'extracted': 'data/processed/extracted',
    'int_encoded': 'data/processed/int_encoded',
    'one_hot_encoded': 'data/processed/one_hot_encoded',
    'encodings': 'data/encodings',
    }

def get_data(
    stage='int_encoded', 
    split=['train', 'dev', 'test'], 
    subsample=math.inf):
  """Load specified data into memory.
  
  Parameters
  ----------
  stage : str 
    Load data from different stages into memory. Stages are:
    1. Raw 
       Raw Review Data - received in JSON format
    2. Extracted 
       Extracted Review Summary and Text and saved the
       tokenised versions. Can be loaded into a list of list
       of strings.
       The gold standard sentiment analysis is stored as
       a list of strings.
    3. Int-Encoded
       An integer-encoding mapping from the extracted training
       samples that was used to integer encode both the
       list of movie reviews and the sentiments. 
    4. One-Hot Encoded
       Converted the integer encoded movie reviews (each
       review is a sequence of tokens in the length of the
       review) into one-hot encoded vectors in the length of
       the entire training vocabulary. 

  split : tuple or str
    Specify which split to load. If received data type is
    tuple, then all valid splits are loaded in the order
    received through the tuple.
    If the data type is a string, then the method just
    returns the data from this split.
    For each split a tuple of the format
    `(X_{split}, y_{split})` for the specified stage of
    preprocessing is loaded.

  Returns
  -------
  For stage `raw`:
    raw : dict
      Dictionary representing the raw data saved as JSON 
      object

  For stage `extracted`:
    X_extracted : list[list[str]] 
      Returns each review as a list of tokens. 
    y_extracted : list[str]
      Returns the sentiment for each review as a string

  For stage `int_encoded`:
    X_encoded : list[list[int]] 
      Returns each review as a list of integers,
      representing the original tokens. Mapped with
      word2idx dictionary.
    y_encoded : list[int]
      Returns the sentiment for each review as an integer.
      Mapped with label2idx dictionary.

  For stage `one_hot_encoded`:
    X_encoded : np.array(N, V)
      Returns each review as a one hot encoded vectors in
      the vocabulary size. 
    y_encoded : np.array[int]
      Returns the sentiment for each review as an integer.
      Mapped with label2idx dictionary.
  """

  # check input
  assert type(stage) == str
  if stage not in ['raw', 'extracted', 'int_encoded', 'one_hot_encoded']:
    raise ValueError(f"{stage} is an invalid stage")

  assert type(split) in (list, str) 
  if type(split) == list:
    for s in split:
      if s not in ['train', 'dev', 'test']:
        raise ValueError(f"{s} is an invalid split")
  else:
      if split not in ['train', 'dev', 'test']:
        raise ValueError(f"{split} is an invalid split")
      split = [split]

  # prepare return data
  res = [None, None] * len(split) 

  # load and return data
  if stage == 'raw':
    res = [None] * len(split)
    path = DATA['raw']
    for i, s in enumerate(split):
      if s == 'test':
        raw = _load_json_gz(f"{path}/music_reviews_{s}_masked.json.gz")
      else:
        raw = _load_json_gz(f"{path}/music_reviews_{s}.json.gz")
      res[i] = raw

    return res if len(res) > 1 else res[0]
  
  if stage == 'extracted':
    path = DATA['extracted']
    for i, s in enumerate(split):
      X = _load_data(f"{path}/X_{s}.tsv")
      y = _load_data(f"{path}/y_{s}.tsv", one_dim=True)
      res[2*i] = X
      res[2*i+1] = y 

    return res if len(res) > 1 else res[0]

  if stage == 'int_encoded':
    path = DATA['int_encoded']
    for i, s in enumerate(split):
      X = _load_data(f"{path}/X_{s}.csv", sep=',', dtype=int)
      y = _load_data(f"{path}/y_{s}.csv", sep=',', dtype=int, one_dim=True)
      res[2*i] = X
      res[2*i+1] = y 

    return res if len(res) > 1 else res[0]

  if stage == 'one_hot_encoded':
    path = DATA['one_hot_encoded']
    for i, s in enumerate(split):
      X = load_npz(f"{path}/X_{s}.npz")
      y = np.array(_load_data(f"{path}/y_{s}.csv", sep=',',
        one_dim=True))
      res[2*i] = X
      res[2*i+1] = y 

    return res if len(res) > 1 else res[0]

def get_encodings(which='word2idx'):
  assert type(which) in (list, str)
  if type(which) == str: which = [which]
  res = [None]*len(which)
  path = DATA['encodings']
  for i, enc in enumerate(which):
    res[i] = _load_json(f"{path}/{enc}.json")
  return res if len(res) > 1 else res[0]

def _load_data(path, dtype=str, sep='\t', one_dim=False, subsample=math.inf):
  data = []
  with open(path, 'r') as infile:
    for i, line in enumerate(infile):
      line = list(map(dtype, [t for t in line.strip().split(sep) if t != '']))
      if one_dim:
        line = dtype(line[0])
      data.append(line)

      if i >= subsample:
        break
  return data

def _load_json(path):
  with open(path, 'r') as infile:
    return json.loads(infile.read())

def _load_json_gz(path, subsample=math.inf):
  data = []
  for i, line in enumerate(gzip.open(path)):
    review_data = json.loads(line)
    data.append(review_data)
    
    if i >= subsample:
      break
  return data