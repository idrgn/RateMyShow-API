from django.http import JsonResponse


def sessions(r):
    if r.method == "POST":
        return JsonResponse(
            {"sessionToken": "ASDFASDFASDFLASKDF"},
            json_dumps_params={"ensure_ascii": False},
            status=201,
        )
    elif r.method == "DELETE":
        return JsonResponse(status=200)


def get_user_by_name(r, username):
    if r.method == "GET":
        return JsonResponse(
            {
                "username": "no usename",
                "name": "Paco",
                "surname": "Martínez",
                "email": "asdfasdf@asdfasdf.sdf",
                "phone": "9812938712",
                "numFollowers": 50,
                "numFollowing": 10,
                "avatarId": 5,
                "favorites": [
                    {
                        "id": "tt0287764",
                        "title": "Three Dogs",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": "tt0287782",
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                ],
                "pending": [
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                    {
                        "id": 1,
                        "title": "Jingle Christmas",
                        "year": 2000,
                        "dateAdded": "2022-12-12T10:00:00Z",
                    },
                ],
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_follow_by_name(r, username):
    if r.method == "GET":
        return JsonResponse(
            [
                {"username": "Usuario 1", "name": "Jaime", "avatarId": 1},
                {"username": "Usuario 2", "name": "Paco", "avatarId": 2},
                {"username": "Usuario 3", "name": "Juan", "avatarId": 3},
                {"username": "Miguel", "name": "Miguel", "avatarId": 4},
                {"username": "Quique", "name": "Kike", "avatarId": 5},
                {"username": "Sara", "name": "Sara", "avatarId": 6},
                {"username": "Usuario 7", "name": "Alfonso", "avatarId": 7},
                {"username": "Usuario 8", "name": "Obama", "avatarId": 8},
                {"username": "Usuario 9", "name": "Stalin", "avatarId": 9},
                {"username": "Usuario 10", "name": "Martín", "avatarId": 10},
                {"username": "Usuario 11", "name": "María", "avatarId": 11},
                {"username": "Usuario 12", "name": "Antía", "avatarId": 12},
                {"username": "Usuario 13", "name": "Rubén", "avatarId": 13},
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def get_ratings_by_name(r, username):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": "tt0903747",
                    "title": "Breaking Bad",
                    "year": 2010,
                    "rating": 4.5,
                    "dateAdded": "2022-12-12T10:00:00Z",
                },
                {
                    "id": "tt0287635",
                    "title": "Pokemon 4Ever",
                    "year": 2020,
                    "rating": 3.5,
                    "dateAdded": "2021-12-12T10:00:00Z",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def follow(r):
    if r.method == "PUT":
        return JsonResponse(
            status=200,
        )
    if r.method == "DELETE":
        return JsonResponse(
            status=200,
        )


def feed(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": "tt0903747",
                    "title": "Breaking Bad",
                    "byUser": "Miguel",
                    "comment": "Está mal",
                    "year": 2010,
                    "rating": 4.5,
                    "dateAdded": "2022-12-12T10:00:00Z",
                },
                {
                    "id": "tt0287635",
                    "title": "Pokemon 4Ever",
                    "byUser": "Miguel",
                    "comment": "Está bien",
                    "year": 2020,
                    "rating": 3.5,
                    "dateAdded": "2021-12-12T10:00:00Z",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def best_rated(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": "tt0903747",
                    "title": "Breaking Bad",
                    "year": 2010,
                    "rating": 4.5,
                },
                {
                    "id": "tt0287635",
                    "title": "Pokemon 4Ever",
                    "year": 2020,
                    "rating": 3.5,
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def recommendations(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "genre": "Action",
                    "titles": [
                        {
                            "id": 1,
                            "title": "Jingle Christmas",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Avatar",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Misión Imposible",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Avatar",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Misión Imposible",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                    ],
                },
                {
                    "genre": "Comedia",
                    "titles": [
                        {
                            "id": 1,
                            "title": "Como Dios",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Jumanji",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Friends",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Jumanji",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Friends",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                    ],
                },
                {
                    "genre": "Drama",
                    "titles": [
                        {
                            "id": 1,
                            "title": "Titanic",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "El diario de Noa",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Lo imposible",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "Titanic",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                        {
                            "id": 1,
                            "title": "El diario de Noa",
                            "year": 2000,
                            "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                        },
                    ],
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def latest(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Lo imposible",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def favorites(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Lo imposible",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def pending(r):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Lo imposible",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def titles_by_query(r, query):
    if r.method == "GET":
        return JsonResponse(
            [
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Lo imposible",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "Titanic",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
                {
                    "id": 1,
                    "title": "El diario de Noa",
                    "year": 2000,
                    "cover": "https://lumiere-a.akamaihd.net/v1/images/image_b88fdde2.jpeg?region=0,0,540,810&width=480",
                },
            ],
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def pending_by_id(r, title_id):
    if r.method == "PUT":
        return JsonResponse(
            status=200,
        )
    if r.method == "DELETE":
        return JsonResponse(
            status=200,
        )

def favorite_by_id(r, title_id):
    if r.method == "PUT":
        return JsonResponse(
            status=200,
        )
    if r.method == "DELETE":
        return JsonResponse(
            status=200,
        )

def rating(r, title_id):
    if r.method == "PUT":
        return JsonResponse(
            status=200,
        )
