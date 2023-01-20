import csv

# Almacenamiento de datos de las tablas Participants y ParticipantCategory de la BBDD

data = []
count = 1
last_checked = ""
last_checked_is = None
categories = []
person_ids = []

with open("filtered/TitleIDs.txt") as file:
    title_ids = [line.rstrip() for line in file]
    subject_set = frozenset(title_ids)

with open("title.principals.tsv", encoding="utf-8") as tsvfile:

    reader = csv.reader(tsvfile, delimiter="\t")

    for row in reader:
        titleId = row[0]

        if titleId != last_checked:
            last_checked = titleId
            last_checked_is = titleId in subject_set

        if last_checked_is:
            print(count)

            data.append(
                {"id": count, "titleId": row[0], "personId": row[2], "category": row[3]}
            )

            category = row[3].lower()
            if category == "\\n":
                category = "none"
            if category not in categories:
                categories.append(category)

            count += 1


with open("filtered/Participants.tsv", "wt", encoding="utf8") as out_file:
    tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["id", "titleId", "personId", "category"])
    for entry in data:
        category = entry["category"].lower()
        tsv_writer.writerow(
            [
                entry["id"],
                entry["titleId"],
                entry["personId"],
                categories.index(category) + 1,
            ]
        )

with open("filtered/ParticipantCategory.tsv", "wt", encoding="utf8") as out_file:
    tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["id", "category"])
    for entry in categories:
        tsv_writer.writerow([categories.index(entry) + 1, entry])
