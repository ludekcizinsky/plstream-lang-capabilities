# _mispredictions.py
# script to extract the analyse the wrong predictions of the
# baseline model
from scripts.utils import output, working_on, finished
from scripts.utils import get_data, get_encodings, load_model
from scripts.baseline import LogisticRegression

import os
import numpy as np
from timeit import default_timer as timer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

def identify_mispredictions():
  # loading data
  total = timer()
  start = working_on('Loading Train and Dev Data')

  # loading textual dev reviews
  X_train, y_train, X_dev, y_dev = get_data(stage='extracted', split=['train', 'dev'])

  # loading training and dev one hot encoded
  word2idx, idx2label = get_encodings(['word2idx', 'idx2label'])
  label2idx, word2idx = get_encodings(['label2idx', 'word2idx'])

  # int encoding labels
  y_train = [label2idx[label] for label in y_train]
  y_dev = [label2idx[label] for label in y_dev]

  finished('Loading Train and Dev Data', timer() - start)

  # logistic regression baseline
  start = working_on('Predicting on Validation Split')
  model = load_model('data/models/logistic_regression.pkl')

  preds = model.predict(X_dev)
  print(f">> Validation Accuracy: {accuracy_score(y_dev, preds)}")
  print(f">> False Positives :\n{confusion_matrix(y_dev, preds)[0, 1]}") 
  print(f">> False Negatives :\n{confusion_matrix(y_dev, preds)[1, 0]}") 
  finished('Predicting on Validation Split', timer()-start)

  # saving difficult cases
  start = working_on('Finding Mispredictions')
  path = 'results/mispredictions'
  os.makedirs(path) if not os.path.exists(path) else None
  with open(f"{path}/mispredictions.txt", "w") as outfile:
    for i in range(len(y_dev)):
      if preds[i] != y_dev[i]:
        review = X_dev[i]
        pred = 'positive' if int(preds[i]) else 'negative'
        true = 'positive' if int(y_dev[i]) else 'negative'
        outfile.write(f"{review} - {pred} ({true})\n")
  finished('Finding Mispredictions', timer()-start)

  finished('Entire Difficult Cases Pipeline', timer()-total)

