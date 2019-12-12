def merge_lines():

    with open("label_list.txt") as oldfile, open("labels_merged.txt", 'w') as newfile:
        for line in oldfile:
            newfile.write(line.rstrip())

merge_lines()