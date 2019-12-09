from arff import Arff
import numpy as np
from sklearn.neural_network import MLPClassifier
from splitter import split
from warnings import filterwarnings
filterwarnings('ignore')

mat = Arff("default.arff",label_count=0)
print("parsed")

data = mat.data[:,:-1]
labels = mat.data[:,-1:]
data, labels = np.random.shuffle(data, labels)
data, labels, test_data, test_labels = split(data, labels, .75)

layer_size = 2
learning_rate = .1
momentum = .5

for i in range(1,10):
        for j in range(1,i+1):
                hidden_layer_sizes = [i] * j
                clf = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, max_iter=500, 
                        learning_rate='constant', solver='sgd')

                clf.fit(data,labels)
                print(i,j, clf.score(test_data,test_labels))