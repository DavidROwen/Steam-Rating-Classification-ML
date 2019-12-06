
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

def remove(labels, old, new):

    with open(old) as oldfile, open(new, 'w') as newfile:
        for line in oldfile:
            if not any(bad_label in line for bad_label in labels):
                newfile.write(line)

remove(["Mixed", "Mostly_Negative", "Negative", "Very_Negative", "Overwhelmingly_Negative"], "default.arff", "goodGames.arff")