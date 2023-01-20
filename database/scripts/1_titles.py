import csv
import random

# Almacenamiento de datos de las tablas GenreTypes, TitleTypes, Genres y Titles de la BBDD
# También alamacena un documento de texto con las IDs de los títulos disponibles en la BBDD

title_ids = []

with open("title.basics.tsv", encoding="utf-8") as tsvfile:

    reader = csv.reader(tsvfile, delimiter="\t")

    data = []
    titleTypes = []
    genres = []

    for row in reader:
        try:
            year = int(row[5])
        except Exception as e:
            continue

        type = row[1]
        title_genres = row[8].lower().split(",")

        if type not in titleTypes:
            titleTypes.append(type)

        for genre in title_genres:
            if genre == "\\n":
                genre = "none"
            if genre not in genres:
                genres.append(genre)

        if year >= 1990 and type in ["movie", "tvMovie", "series", "tvSeries"]:
            data.append(
                {
                    "id": row[0],
                    "titleType": row[1],
                    "primaryTitle": row[2],
                    "originalTitle": row[3],
                    "isAdult": row[4],
                    "startYear": row[5],
                    "endYear": row[6],
                    "runtimeMinutes": row[7],
                    "genres": row[8],
                }
            )


print(f"Genres: {genres}")
with open("filtered/GenreTypes.tsv", "wt", encoding="utf8") as out_file:
    tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["id", "genre"])
    for genre in genres:
        tsv_writer.writerow([genres.index(genre) + 1, genre])

print(f"Title types: {titleTypes}")
with open("filtered/TitleTypes.tsv", "wt", encoding="utf8") as out_file:
    tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["id", "name"])
    for type in titleTypes:
        tsv_writer.writerow([titleTypes.index(type) + 1, type])

language_list = ["es", "en", "zh", "hi", "fr", "ar", "bn", "ru", "pt", "id"]

for _ in range(50):
    language_list.append("en")

for _ in range(10):
    language_list.append("es")

for _ in range(10):
    language_list.append("zh")

for _ in range(5):
    language_list.append("fr")

with open("filtered/Genres.tsv", "wt", encoding="utf8") as out_file_genre:
    tsv_writer_genre = csv.writer(out_file_genre, delimiter="\t", lineterminator="\n")
    count = 1
    tsv_writer_genre.writerow(
        [
            "id",
            "titleId",
            "genreId",
        ]
    )

    with open("filtered/Titles.tsv", "wt", encoding="utf8") as out_file:
        tsv_writer = csv.writer(out_file, delimiter="\t", lineterminator="\n")
        tsv_writer.writerow(
            [
                "id",
                "titleType",
                "primaryTitle",
                "originalTitle",
                "startYear",
                "endYear",
                "runtimeMinutes",
                "language",
            ]
        )

        for title in data:
            split_genres = title["genres"].lower().split(",")
            new_genre_list = ""
            for genre in split_genres:
                if genre == "\\n":
                    genre = "none"
                tsv_writer_genre.writerow(
                    [
                        count,
                        title["id"],
                        genres.index(genre) + 1,
                    ]
                )
                count += 1

            new_genre_list = new_genre_list[:-1]

            title_ids.append(title["id"] + "\n")

            tsv_writer.writerow(
                [
                    title["id"],
                    titleTypes.index(title["titleType"]) + 1,
                    title["primaryTitle"],
                    title["originalTitle"],
                    title["startYear"],
                    title["endYear"],
                    title["runtimeMinutes"],
                    random.choice(language_list),
                ]
            )

f = open("filtered/TitleIDs.txt", "w")
f.writelines(title_ids)
f.close()
