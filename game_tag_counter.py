from arff import Arff
import numpy as np
from sklearn.neural_network import MLPClassifier
from my_shuffling import shuffle
from splitter import split
from warnings import filterwarnings
filterwarnings('ignore')

mat = Arff("default.arff",label_count=0)
print("parsed")

sum_of_incorrect_labels = 0
max_counted = 0
most_common_data_indexes = None
data = mat.data[:,:-1]
labels = mat.data[:,-1:]

unique_data = np.unique(data, axis=0)
for ud in unique_data:
    indexes = np.where((data == ud).all(axis=1))[0]
    labels_for_same_game = labels[indexes]
    labels_for_same_game = np.unique(labels_for_same_game, return_counts=True)
    if len(labels_for_same_game[1]) > 1:
        maximum_indx = np.argmax(labels_for_same_game[1])
        incorrect_count = sum(labels_for_same_game[1]) - labels_for_same_game[1][maximum_indx]
        sum_of_incorrect_labels += incorrect_count
        # print(sum_of_incorrect_labels)

        if sum(labels_for_same_game[1]) > max_counted:
            max_counted = sum(labels_for_same_game[1])
            most_common_data_indexes = indexes
            print("found new most counted: " + str(max_counted))
print(most_common_data_indexes)
print(max_counted)
print("finished") # 2054 games will be incorrectly predicted (2054/19173% = 10.71% accuracy loss gaurentee)