
# { 
#     Overwhelmingly_Positive, 
#     Very_Positive, 
#     Positive, 
#     Mostly_Positive, 
#     Mixed, 
#     Mostly_Negative, 
#     Negative, 
#     Very_Negative, 
#     Overwhelmingly_Negative
# }

def remove_labels(labels_keep, labels_throw, old, new):

    with open(old) as oldfile, open(new, 'w') as newfile:
        for line in oldfile:
            if any(label in line for label in labels_keep) or not any(bad_label in line for bad_label in labels_throw):
                newfile.write(line)

remove_labels(["Very", "Overwhelmingly", "Mixed"],["Negative", "Positive"], "default.arff", "oldgames.arff")