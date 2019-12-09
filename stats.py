import numpy as np
from arff import Arff

mat = Arff("default.arff", label_count=1)
unique, counts = np.unique(mat.data[:,-1], return_counts=True)
print(dict(zip(unique, counts)))