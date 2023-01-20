import csv

# Almacenamiento de los datos de la tabla Nombres usados en la BBDD

data = []

with open("filtered/PersonIDs.txt") as file:
    person_ids = [line.rstrip() for line in file]
    subject_set = frozenset(person_ids)


with open("name.basics.tsv", encoding="utf-8") as tsvfile:
    reader = csv.reader(tsvfile, delimiter="\t")

    for row in reader:
        nameId = row[0]

        if nameId in subject_set:
            data.append(
                {
                    "id": row[0],
                    "name": row[1],
                }
            )

            print(row[0])

with open("filtered/Names.tsv", "wt", encoding="utf8") as out_file:
    tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["id", "name"])
    for entry in data:
        tsv_writer.writerow([entry["id"], entry["name"]])
