import numpy as np
import scipy.io
import pickle
import sklearn.linear_model
from sklearn import cross_validation
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from multiprocessing import Pool
import matplotlib.pyplot as plt
import time
import os
import argparse

def extract_features():
  # TODO
  # Given the data sets and phi type and parameters, make the features and features file used for the below function
  pass

"""
These variables and functions must be defined at the top level to work with the pool
Every variable and function below this point belongs to make_plot_from_features
"""
lines = None
labels = None

def accuracy_metric(train_X, train_y, test_X, test_y):
        start = time.time()
        print("Starting accuracy_metric calculation...")

        model = SVC(class_weight='balanced',C=0.5)
        #model = sklearn.linear_model.LogisticRegression()
        #model = GradientBoostingClassifier()

        model.fit(train_X, train_y)
        pred = model.predict(test_X)

        correct_matrix = (pred == test_y)
        accuracy = float(correct_matrix.sum()) / float(correct_matrix.size)

        print("Accuracy: ", accuracy, " Time: ", time.time()-start)
        return accuracy


def cross_validated_accuracy_metric(X, y, num_fold=5, random_seed=0):
    kf = cross_validation.KFold(n=y.size, n_folds=num_fold, shuffle=True,
                            random_state=random_seed)
    accuracy_metrics = [accuracy_metric(X[train_ind], y[train_ind], X[test_ind], y[test_ind]) for train_ind, test_ind in kf]
    return np.mean(accuracy_metrics)

def compute_one_point(X, labels, phi_param):
      print(X.shape, labels.shape, phi_param)
      print("Computing accuracy for phi parameter: ", phi_param)
      accuracy_metric_score = cross_validated_accuracy_metric(X, labels)
      return (phi_param, accuracy_metric_score)

def load_line(index):
    line = lines[index]
    print("Loading line: ", line)
    split_line = line.split(",")
    assert (len(split_line) == 2), "The features file should have one comma per line"
    assert os.path.exists(split_line[0]), "One of the feature paths supplied does not exists"

    X = np.load(split_line[0])

    if split_line[1][-1] == '\n':
      split_line[1] = split_line[1][:-1]
    phi_param = float(split_line[1])

    print("Loaded phi: ", phi_param)
    return compute_one_point(X, labels, phi_param)


def make_plot_from_features(features_file, labels_file, out_file_name="phi_plot", title=None):
  # A file with comma separated values, each row contrains (absolute path to the features numpy array, phi parameter value used on the x axis)
  # The phi parameter should be a single number floating point or integer
  # file path to labels - either a numpy array or a .txt file in range [0, num classes)
  # The plot title

  global lines, Xs, phi_params, labels

  assert not os.path.exists(out_file_name)
  assert not os.path.exists(out_file_name + ".png")

  # load features_file, multi thread
  print("Reading features file: ", features_file)
  lines = []
  with open(features_file) as f:
    for line in f:
      lines.append(line)

  print("Loading the following files: ")
  for line in lines:
    print(line)

  # load labels file
  print("Reading labels file: ", labels_file)
  print("File extension: ", labels_file[-4:])
  if labels_file[-4:] == ".npy":
    labels = np.load(labels_file)
  else:
    assert labels_file[-4:] == ".txt", "Should be .txt with one label per line or .npy"
    labels = []
    with open(labels_file) as f:
      for line in f:
        if line[-1] == '\n':
          line = line[:-1]
        labels.append(float(line))
    labels = np.array(labels)

  # multi thread
  pool = Pool(40)
  points = pool.map(load_line, range(len(lines)))

  # Produce the plot
  print("Producing plot for: ", out_file_name)
  print("Title is: ", title)

  points = sorted(points)
  print("Points:")
  print(points)
  x_points = np.array([x for x, y in points])
  y_points = np.array([y for x, y in points])
  plt.plot(x_points, y_points)
  if title is not None:
    assert type(title) == type("")
    plt.title(title)
  plt.savefig(out_file_name)
  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'features_file', help='A file where each line is "[1],[2]\n" where [1] is the path to a numpy array of features and [2] is the phi value')
    parser.add_argument(
        'labels_file', help='A numpy array of labels, should correspond to the features in each features array')
    parser.add_argument(
        'out_file', help='The plot file name', default="phi_plot")
    parser.add_argument(
        'title', help="The title of the plot", default=None)
    args = parser.parse_args()
    make_plot_from_features(args.features_file, args.labels_file, args.out_file, args.title)









