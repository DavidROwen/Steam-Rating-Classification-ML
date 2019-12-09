def split(X,y,r):
    l = int(len(X)*r)
    return  X[:l],y[:l], X[l:],y[l:]
