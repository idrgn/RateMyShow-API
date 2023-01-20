import csv

# Almacenamiento de IDs de personas usadas en la BBDD

data = []

with open("filtered/Participants.tsv", encoding="utf-8") as tsvfile:
    reader = csv.reader(tsvfile, delimiter="\t")

    for row in reader:
        personId = row[2]
        data.append(personId + "\n")

with open("filtered/PersonIDs.txt", "w") as f:
    f.writelines(data)
