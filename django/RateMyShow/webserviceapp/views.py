import datetime
import json
import math
from random import choice

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from RateMyShow import settings

from .database import get_new_token, get_title, get_user
from .models import (
    Avatars,
    Favorites,
    Followers,
    Genres,
    Pending,
    Ratings,
    Titles,
    Titletypes,
    Tokens,
    Users,
)

"""Vistas de RateMyShow"""


# Cantidad de resultados por página
amount_per_page = 15


def get_page(r):
    # Se obtiene la página actual
    page = r.GET.get("page", 0)

    # Si es string, intenta convertirla a número
    if isinstance(page, str):
        try:
            page = int(page)
        except Exception:
            page = 0

    # Limitar valor mínimo
    if page < 0:
        page = 0

    return page


def get_token_user(r):
    # Se intenta obtener el SessionToken de los headers
    try:
        session_token = r.headers["SessionToken"]
    except Exception:
        return None

    # Intenta buscar el usuario en la BBDD
    try:
        token = Tokens.objects.get(token=session_token)
        return token.userid
    except ObjectDoesNotExist:
        return None


def get_most_common_elements(list):
    element_counts = {}
    for element in list:
        if element in element_counts:
            element_counts[element] += 1
        else:
            element_counts[element] = 1
    sorted_element_counts = sorted(
        element_counts.items(), key=lambda x: x[1], reverse=True
    )
    return [item[0] for item in sorted_element_counts]


def title_search(r):
    if r.method == "GET":
        # Se obtienen los parámetros de URL
        query = r.GET.get("query", None)

        # Se obtiene la página actual
        page = get_page(r)

        # Se obtienen los resultados
        if query == None:
            search = Titles.objects.all().order_by(
                "-imdbratingcount", "-imdbrating", "-startyear"
            )
        else:
            search = Titles.objects.filter(
                Q(primarytitle__icontains=query)
                | Q(originaltitle__icontains=query)
                | Q(translatedtitle__icontains=query)
            ).order_by("-imdbratingcount", "-imdbrating", "-startyear")

        # Almacenar cantidad total
        total = search.count()

        # Si no hay respuestas, devuelve un 404
        if total == 0:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se almacenan los datos de cada título en una lista
        result_list = []
        current_user = get_token_user(r)
        for title in search[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list.append(get_title(title.id, current_user))

        # Se devuelve la lista
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "result": result_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def best_rated(r):
    if r.method == "GET":
        # Se obtiene la página actual
        page = get_page(r)

        # Se obtienen los títulos que tienen un rating
        titles = (
            Ratings.objects.all()
            .values("titleid")
            .annotate(average_rating=Avg("rating"))
            .annotate(rating_count=Count("rating"))
            .order_by("-average_rating", "-rating_count")
        )

        # Almacenar cantidad total
        total = titles.count()

        # Se almacenan los datos de cada título en una lista
        result_list = []
        current_user = get_token_user(r)
        for title in titles[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list.append(get_title(title["titleid"], current_user))

        # Se devuelve la lista
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "result": result_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_title_by_id(r, title_id):
    if r.method == "GET":
        # Obtiene el título
        try:
            response = get_title(title_id, get_token_user(r))
        except Exception:
            response = None

        # Si la respuesta es None, envía un status 404 (Not found)
        if response == None:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se envía la respuesta con status 200 (OK)
        return JsonResponse(
            response, json_dumps_params={"ensure_ascii": False}, status=200
        )


def get_random_title(r):
    if r.method == "GET":
        # Se obtienen todas las claves primarias de la tabla Titles
        pks = Titles.objects.values_list("pk", flat=True)

        # Se selecciona una de las claves
        random_pk = choice(pks)

        # Devuelve los datos
        return JsonResponse(
            get_title(random_pk, get_token_user(r)),
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


@csrf_exempt
def search_register_user(r):
    if r.method == "POST":
        # Se intenta obtener el cuerpo de la petición
        try:
            data = json.loads(r.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"message": "Bad request"}, status=400)

        # Si el número de teléfono está vacío, se asigna None(null)
        if data["phone"] == "":
            data["phone"] = None

        # Se intenta obtener el usuario de la BBDD con los datos obtenidos
        # - Solo se obtiene con el teléfono si el campo no es null
        user_exists = Users.objects.filter(
            (Q(phone__isnull=False) & Q(phone=data["phone"]))
            | Q(username=data["username"])
            | Q(email=data["email"])
        ).exists()

        # Si el usuario existe en la BBDD, conflicto
        if user_exists:
            return JsonResponse(
                {"message": "User already exists"},
                json_dumps_params={"ensure_ascii": False},
                status=409,
            )

        # Si los datos no existen, 400
        if not data["username"] or not data["email"]:
            return JsonResponse({"message": "Bad request"}, status=400)

        # Se añade el usuario a la BBDD
        user = Users()
        user.username = data["username"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.birthdate = data["birthDate"]
        user.name = data["name"]
        user.surname = data["surname"]

        # Se añade la fecha actual como fecha de registro
        user.registerdate = datetime.datetime.now()

        # Se obtienen todas las claves primarias de la tabla Avatars
        avatar_ids = Avatars.objects.values_list("pk", flat=True)

        # Se asigna un avatar aleatorio
        user.avatarid = Avatars.objects.get(pk=choice(avatar_ids))

        # Se asigna la contraseña encriptada
        user.set_password(data["password"])

        # Se guarda el usuario
        user.save()

        # Se genera el token
        token_string = get_new_token()
        new_token = Tokens()
        new_token.token = token_string
        new_token.userid = user
        new_token.save()

        # Se devuelve un 201
        return JsonResponse(
            {"sessionToken": token_string},
            json_dumps_params={"ensure_ascii": False},
            status=201,
        )

    elif r.method == "GET":
        query = r.GET.get("query", None)

        # Se obtiene la página actual
        page = get_page(r)

        # Se obtienen los resultados
        if query:
            search = Users.objects.filter(
                Q(username__icontains=query)
                | Q(name__icontains=query)
                | Q(surname__icontains=query)
            ).order_by("-registerdate")
        else:
            search = Users.objects.all().order_by("-registerdate")

        # Almacenar cantidad total
        total = search.count()

        # Se almacenan los datos de cada título en una lista
        user_list = []
        current_user = get_token_user(r)
        for user in search[amount_per_page * page : amount_per_page * (page + 1)]:
            user_list.append(get_user(user, current_user))

        # Se devuelve la lista
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "users": user_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


@csrf_exempt
def sessions(r):
    # Si el método es POST, se intenta crear una nueva sesión
    if r.method == "POST":

        # Se intenta obtener el cuerpo de la petición
        try:
            data = json.loads(r.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"message": "Bad request"}, status=400)

        # Se intenta obtener el usuario de la BBDD con los datos obtenidos
        # - Solo se obtiene con el teléfono si el campo no es null
        try:
            user = Users.objects.get(
                (Q(phone__isnull=False) & Q(phone=data["identifier"]))
                | Q(username=data["identifier"])
                | Q(email=data["identifier"])
            )
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se intenta verificar la contraseña
        if user.check_password(data["password"]):
            # Se genera el token
            token_string = get_new_token()
            new_token = Tokens()
            new_token.token = token_string
            new_token.userid = user
            new_token.save()

            # Se devuelve un 201
            return JsonResponse(
                {"sessionToken": token_string},
                json_dumps_params={"ensure_ascii": False},
                status=201,
            )
        else:
            # Se devuelve 401
            return JsonResponse({"message": "Unauthorized"}, status=401)

    # Si el método es DELETE, se intenta borrar la sesión
    elif r.method == "DELETE":

        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Se intenta obtener el token de la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se elimina el token
        token.delete()

        # Respuesta: 200
        return JsonResponse({"message": "OK"}, status=200)

    # Si el método es GET se obtiene el usuario de la sesión
    elif r.method == "GET":

        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Se intenta obtener el token de la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Devuelve los datos del usuario
        return JsonResponse(
            get_user(token.userid, get_token_user(r)),
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_user_by_name(r, username):
    if r.method == "GET":
        # Intenta buscar el usuario en la BBDD
        try:
            user = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        return JsonResponse(
            get_user(user, get_token_user(r), get_fav_pending=True),
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


@csrf_exempt
def favorite_by_id(r, title_id):
    if r.method == "PUT":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Comprueba que el favorito no existe en la BBDD
        favorite_exists = Favorites.objects.filter(
            userid=token.userid, titleid=title_id
        ).exists()
        if favorite_exists:
            return JsonResponse({"message": "Conflict"}, status=409)

        # Añade titulo a favoritos
        favorite = Favorites()
        favorite.userid = token.userid
        favorite.titleid = Titles.objects.get(pk=title_id)
        favorite.addeddate = datetime.date.today()
        favorite.save()
        return JsonResponse({"message": "OK"}, status=200)

    if r.method == "DELETE":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Elimina titulo de favoritos
        try:
            favorite = Favorites.objects.filter(userid=token.userid, titleid=title_id)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        favorite.delete()
        return JsonResponse({"message": "OK"}, status=200)


@csrf_exempt
def pending_by_id(r, title_id):
    if r.method == "PUT":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Comprueba que el pendiente no existe en la BBDD
        pending_exists = Pending.objects.filter(
            userid=token.userid, titleid=title_id
        ).exists()
        if pending_exists:
            return JsonResponse({"message": "Conflict"}, status=409)

        # Añade titulo a pendientes
        pending = Pending()
        pending.userid = token.userid
        pending.titleid = Titles.objects.get(pk=title_id)
        pending.addeddate = datetime.date.today()
        pending.save()
        return JsonResponse({"message": "OK"}, status=200)

    if r.method == "DELETE":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Elimina titulo de pendientes
        try:
            pending = Pending.objects.filter(userid=token.userid, titleid=title_id)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        pending.delete()
        return JsonResponse({"message": "OK"}, status=200)


def get_followers_by_name(r, username):
    if r.method == "GET":
        try:
            # Obtiene el usuario
            user = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            # Si genera un error al obtener el usuario, devuelve notfound
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Obtiene todos los seguidores del usuario
        followers = Followers.objects.filter(followedid=user).order_by("-addeddate")

        # Se obtiene el total de seguidores
        total = followers.count()

        follower_list = []
        current_user = get_token_user(r)
        for follower in followers[
            amount_per_page * page : amount_per_page * (page + 1)
        ]:
            # Convierte el objeto dictionary a json
            dictionary = get_user(follower.followerid, current_user)

            # Se añade dictionary
            follower_list.append(dictionary)

        # Devuelve la lista de seguidores
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "followers": follower_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_following_by_name(r, username):
    if r.method == "GET":
        try:
            # Obtiene el usuario
            user = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            # Si genera un error al obtener el usuario, devuelve notfound
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Obtiene todos los usuarios a los que sigue el usuario
        following = Followers.objects.filter(followerid=user).order_by("-addeddate")

        # Se obtiene el total de seguidos
        total = following.count()

        following_list = []
        current_user = get_token_user(r)
        for followed in following[
            amount_per_page * page : amount_per_page * (page + 1)
        ]:
            # Convierte el objeto dictionary a json
            dictionary = get_user(followed.followedid, current_user)

            # Se añade dictionary
            following_list.append(dictionary)

        # Devuelve la lista de seguidos
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "following": following_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_favorites(r):
    if r.method == "GET":

        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Se intenta obtener el token de la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Obtener lista de favoritos
        favorites = Favorites.objects.filter(userid=token.userid).order_by("-addeddate")
        favorites_list = []

        # Se obtiene el total de favoritos
        total = favorites.count()

        # Se almacenan los datos de cada título en una lista
        current_user = get_token_user(r)
        for favorite in favorites[
            amount_per_page * page : amount_per_page * (page + 1)
        ]:
            favorites_list.append(get_title(favorite.titleid.pk, current_user))

        # Devuelve la lista de favoritos
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "favorites": favorites_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_pending(r):
    if r.method == "GET":

        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Se intenta obtener el token de la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Obtener lista de pendientes
        pending = Pending.objects.filter(userid=token.userid).order_by("-addeddate")
        pending_list = []

        # Se obtiene el total de pendientes
        total = pending.count()

        # Se almacenan los datos de cada título en una lista
        current_user = get_token_user(r)
        for item in pending[amount_per_page * page : amount_per_page * (page + 1)]:
            pending_list.append(get_title(item.titleid.pk, current_user))

        # Devuelve la lista de pendientes
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "pending": pending_list,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_feed(r):
    if r.method == "GET":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la base de datos
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Obtiene la lista de seguidos del usuario
        followers = Followers.objects.filter(followerid=token.userid).values(
            "followedid"
        )

        # Obtiene los ratings de los usuarios
        ratings = Ratings.objects.filter(
            Q(posterid__in=followers) | Q(posterid=token.userid)
        ).order_by("-addeddate")

        # Se obtiene el total de pendientes
        total = ratings.count()

        # Obtiene los datos de los títulos
        feed_data = []
        current_user = get_token_user(r)
        for rating in ratings[amount_per_page * page : amount_per_page * (page + 1)]:
            entry = get_title(rating.titleid.pk, current_user)
            entry["rating"] = rating.rating
            entry["comment"] = rating.comment
            entry["addedDate"] = rating.addeddate
            entry["user"] = get_user(rating.posterid, current_user)
            feed_data.append(entry)

        # Devuelve la lista de pendientes
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "feed": feed_data,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def latest(r):
    if r.method == "GET":
        # Se obtiene la página actual
        page = get_page(r)

        # Se obtiene el tipo de título de película
        try:
            movie_type = Titletypes.objects.filter(name__icontains="movie").values("id")
        except Titletypes.DoesNotExist:
            return JsonResponse(
                {"error": "No se encontró el tipo de título 'movie'"}, status=404
            )

        # Se obtiene el tipo de título de serie
        series_type = Titletypes.objects.filter(name__icontains="serie").values("id")

        # Se obtienen las películas ordenadas por fecha.
        movies = Titles.objects.filter(titletype__in=movie_type).order_by(
            "-startyear", "-imdbratingcount", "-imdbrating"
        )

        # Se obtienen las series ordenadas por fecha.
        series = Titles.objects.filter(titletype__in=series_type).order_by(
            "-startyear", "-imdbratingcount", "-imdbrating"
        )

        # Almacenar cantidad total de películas
        total_movies = movies.count()

        # Almacenar cantidad total de series
        total_series = series.count()

        # Se almacenan los datos de cada título de película en una lista
        result_list_movies = []
        current_user = get_token_user(r)
        for title in movies[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list_movies.append(get_title(title.id, current_user))

        # Se almacenan los datos de cada título de serie en una lista
        result_list_series = []
        for title in series[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list_series.append(get_title(title.id, current_user))

        # Se devuelve la lista
        return JsonResponse(
            {
                "movies": {
                    "total": total_movies,
                    "pages": int(math.ceil(total_movies / amount_per_page)),
                    "current": page,
                    "result": result_list_movies,
                },
                "series": {
                    "total": total_series,
                    "pages": int(math.ceil(total_series / amount_per_page)),
                    "current": page,
                    "result": result_list_series,
                },
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def recommendations(r):
    if r.method == "GET":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtienen los favoritos del usuario
        favorites = Favorites.objects.filter(userid=token.userid).values("titleid")

        # Se obtienen los géneros de los favorios
        favorite_genres = Genres.objects.filter(titleid__in=favorites)

        # Se añaden los favoritos a una lista
        genre_list = []
        for favorite in favorite_genres:
            genre_list.append(favorite.genreid)

        # Se obtienen los 3 géneros qué más aparecen
        top_genres = get_most_common_elements(genre_list)

        response = []

        # Se obtienen títulos de cada género
        current_user = get_token_user(r)
        for genre in top_genres[:3]:
            title_data_list = []

            # Se obtienen los títulos de un género
            title_list = (
                Genres.objects.filter(genreid=genre)
                .order_by(
                    "-titleid__imdbratingcount",
                    "-titleid__imdbrating",
                    "-titleid__startyear",
                )
                .values("titleid")[:5]
            )

            # Se obtienen los datos de los títulos
            for title in title_list:
                title_data_list.append(get_title(title["titleid"], current_user))

            # Se añade el género y los títulos a la respuesta.
            response.append(
                {
                    "genre": genre.genre.rstrip(),
                    "titles": title_data_list,
                }
            )

        return JsonResponse(
            response,
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


@csrf_exempt
def rating(r, title_id):
    if r.method == "PUT":
        # Se intenta obtener el cuerpo de la petición
        try:
            data = json.loads(r.body)

            # Se comprueba que los datos están dentro del límite
            if data["rating"] > 5.0:
                data["rating"] = 5.0
            elif data["rating"] < 0.5:
                data["rating"] = 0.5

            # Si el comentario no es un string, se añade un String vacío
            if not isinstance(data["comment"], str):
                data["comment"] = "Sin comentario"

        except json.decoder.JSONDecodeError:
            return JsonResponse({"message": "Bad request"}, status=400)

        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Intenta buscar el título en la BBDD
        try:
            title = Titles.objects.get(pk=title_id)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Comprueba que el usuario ya no tenga un rating
        has_rating = Ratings.objects.filter(
            titleid=title, posterid=token.userid
        ).exists()

        # No permite añadir mas de 1 rating
        if has_rating:
            return JsonResponse(
                {"message": "User has already rated"},
                status=409,
            )

        # Se crea el rating
        rating = Ratings()
        rating.posterid = token.userid
        rating.titleid = title
        rating.comment = data["comment"]
        rating.rating = data["rating"]
        rating.addeddate = datetime.datetime.now()
        rating.save()

        # Respuesta
        return JsonResponse({"message": "OK"}, status=200)


@csrf_exempt
def follow_user(r, username):
    if r.method == "PUT":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Intenta obtener el usuario a seguir
        try:
            followed = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se comprueba que no es el propio usuario
        if token.userid.pk == followed.pk:
            return JsonResponse(
                {"message": "Already following"},
                json_dumps_params={"ensure_ascii": False},
                status=409,
            )

        # Se comprueba que la entrada no existe
        already_exists = Followers.objects.filter(
            followerid=token.userid, followedid=followed
        ).exists()

        if already_exists:
            return JsonResponse(
                {"message": "Already following"},
                json_dumps_params={"ensure_ascii": False},
                status=409,
            )

        # Se añade a la BBDD
        follower = Followers()
        follower.followedid = followed
        follower.followerid = token.userid
        follower.addeddate = datetime.datetime.now()
        follower.save()

        # Respuesta
        return JsonResponse({"message": "OK"}, status=200)

    if r.method == "DELETE":
        # Se intenta obtener el SessionToken de los headers
        try:
            session_token = r.headers["SessionToken"]
        except Exception:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            token = Tokens.objects.get(token=session_token)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Intenta obtener el usuario a seguir
        try:
            followed = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Obtiene los objetos de la tabla Followers
        result = Followers.objects.filter(followerid=token.userid, followedid=followed)

        if not result.exists():
            return JsonResponse({"message": "Not found"}, status=404)

        # Se eliminan las entradas de la BBDD
        result.delete()

        # Respuesta
        return JsonResponse({"message": "OK"}, status=200)


def get_user_ratings(r, username):
    if r.method == "GET":
        # Se intenta obtener el Usuario
        try:
            user = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Se obtiene los ratings del usuario
        ratings = Ratings.objects.filter(posterid=user).order_by("-addeddate")

        # Almacenar cantidad total
        total = ratings.count()

        # Se obtienen los datos de cada títiulo
        title_data = []
        current_user = get_token_user(r)
        for rating in ratings[amount_per_page * page : amount_per_page * (page + 1)]:
            title = get_title(rating.titleid.pk, current_user)
            # Se añaden los datos del rating
            title["rating"] = rating.rating
            title["comment"] = rating.comment
            title["ratingDate"] = rating.addeddate
            # Se añade a la lista
            title_data.append(title)

        # Respuesta
        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "ratings": title_data,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_profile_picture(r, name):
    try:
        image_data = open(f"{settings.BASE_DIR}/images/profile/{name}.png", "rb").read()
    except FileNotFoundError:
        return JsonResponse({"message": "Not found"}, status=404)

    return HttpResponse(image_data, content_type="image/png")


def get_image(r, name):
    try:
        image_data = open(f"{settings.BASE_DIR}/images/general/{name}.png", "rb").read()
    except FileNotFoundError:
        return JsonResponse({"message": "Not found"}, status=404)

    return HttpResponse(image_data, content_type="image/png")


def get_ratings(r, title_id):
    if r.method == "GET":
        # Intenta buscar el título en la BBDD
        try:
            title = Titles.objects.get(pk=title_id)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = get_page(r)

        # Resultado
        result = Ratings.objects.filter(titleid=title).order_by("-addeddate")

        # Total
        total = result.count()

        ratings = []
        # Se almacenan los ratings
        for rating in result[amount_per_page * page : amount_per_page * (page + 1)]:
            ratings.append(
                {
                    "comment": rating.comment,
                    "rating": rating.rating,
                    "addedDate": rating.addeddate,
                    "username": rating.posterid.username,
                    "avatarId": rating.posterid.avatarid.pk,
                }
            )

        return JsonResponse(
            {
                "total": total,
                "pages": int(math.ceil(total / amount_per_page)),
                "current": page,
                "ratings": ratings,
            },
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )
