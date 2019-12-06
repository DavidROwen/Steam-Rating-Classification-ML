import numpy as np
from arff import Arff
from sklearn import tree
import graphviz 

def sk_learn(data="default.arff"):
    folds = 10
    mat = Arff(data, label_count=1)

    counts = [] ## this is so you know how many types for each column
    for i in range(mat.data.shape[1]):
        counts += [mat.unique_value_count(i)]
    
    np.random.shuffle(mat.data)
    splits = np.array_split(mat.data, folds)
    
    Acc = 0
    min_split = 300
    print("Minsplit: {}".format(min_split))
    for f in range(folds):
        # print("Fold {}:".format(f))
        train = np.array([])
        for other in range(folds):
            if train.size == 0 and other != f:
                train = splits[other].copy()
            elif other != f:
                train = np.concatenate((train, splits[other]))

        data = train[:,0:-1]
        labels = train[:,-1].reshape(-1,1)


        clf = tree.DecisionTreeClassifier(criterion="entropy", min_samples_split=min_split, min_samples_leaf=25)
        clf = clf.fit(data, labels)
        pred = clf.predict(data)
        new_acc = score(pred, labels)
        # print("\tTrain Acc {}".format(new_acc))

        data2 = splits[f][:,0:-1]
        labels2 = splits[f][:,-1].reshape(-1,1)
        pred = clf.predict(data2)
        new_acc = score(pred,labels2)
        # print("\tTest Acc {}".format(new_acc))
        Acc += new_acc

    Acc = Acc / folds
    print("Accuracy = [{:.4f}]".format(Acc))

    # classes =["Overwhelmingly_Positive", "Very_Positive", "Positive", "Mostly_Positive", "Mixed", "Mostly_Negative", "Negative", "Very_Negative", "Overwhelmingly_Negative"]
    # dot_data = tree.export_graphviz(clf, out_file=None, feature_names=mat.get_attr_names()[:-1], class_names=classes, max_depth=6, filled=True, rounded=True)     
    # graph = graphviz.Source(dot_data) 
    # graph.render("wave") 

    return Acc

def score(pred, labels):
    new_acc = 0
    pred = pred.flatten()
    labels = labels.flatten()

    # for i in range(len(pred)):
    #     print("Prediction {}, Label: {}".format(pred[i], labels[i]))
 
    for sample in range(len(pred)):
        if pred[sample] == labels[sample]:
            new_acc += 1
    return new_acc / len(pred)

total_acc = 0
rounds = 4
for _ in range(rounds):
    total_acc += sk_learn()
print("Accuracy = [{:.4f}]".format(total_acc / rounds))
