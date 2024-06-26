import hashlib
import json

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Sum
from django.utils.crypto import get_random_string

from .models import (
    Favorites,
    Followers,
    Genres,
    Participants,
    Pending,
    Ratings,
    Titles,
    Tokens,
    Users,
)

"""Funciones de BBDD de RateMyShow

Funciones de ayuda encargadas de obtener datos de la BBDD que se usarían en varias vistas

Métodos:
 - get_title: obtiene los datos procesados de un título
 - get_new_token: obtiene un token de sesión de usuario no existente en la BBDD
 - get_user: obtiene los datos procesados de un usuario
"""


def simplify_url(url):
    # Elimina los parámetros extra de las URLs de Covers
    target = "_V1_"
    start = url.find(target)
    if start == -1:
        return url
    end = url.rfind("_.", start) + 2
    return url[: start + len(target)] + url[end:]


def get_title(title_id, user: Users = None):
    # Devuelve los datos de un título
    if isinstance(title_id, Titles):
        title = title_id
    else:
        try:
            # Obtiene el título
            title = Titles.objects.get(id=title_id)
        except ObjectDoesNotExist:
            # Si genera un error al obtener el título, revuelve none
            return None

    # Se obtiene el tipo de título
    title_type = title.titletype.name.rstrip()

    # Se obtienen los géneros
    genres = Genres.objects.filter(titleid=title_id)

    # Se añaden a una lista
    genre_list = []
    for genre in genres:
        genre_list.append(genre.genreid.genre.rstrip())

    # Se obtienen las puntuaciones
    all_ratings = Ratings.objects.filter(titleid=title_id)
    rating_average = all_ratings.aggregate(Avg("rating"))
    rating_count = all_ratings.count()

    # Se almacenan los últimos 10 comentarios
    last_comments = []
    for rating in all_ratings.order_by("-addeddate")[0:5]:
        last_comments.append(
            {
                "username": rating.posterid.username,
                "name": rating.posterid.name,
                "surname": rating.posterid.surname,
                "avatarId": rating.posterid.avatarid.pk,
                "comment": rating.comment,
                "rating": rating.rating,
                "addedDate": rating.addeddate,
            }
        )
    # Se obtienen los participantes
    participants = Participants.objects.filter(titleid=title_id)

    # Se añaden a una lista
    participant_list = []
    for participant in participants:
        participant_list.append(
            {
                "name": participant.personid.name.rstrip(),
                "job": participant.category.category.rstrip(),
            }
        )

    # Si los datos adicionales no existen en la BBDD obtienen de la web
    if title.cover == None or title.description == None:

        # Se definen headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            # Se intenta hacer la petición
            request_response = requests.get(
                f"http://www.imdb.com/title/{title_id}/", headers=headers
            )

            # Se procesa la respuesta
            soup = BeautifulSoup(request_response.text, "html.parser")

            try:
                # Opción 1: Se intentan obtener los datos dentro del tag script
                script_tag = soup.find("script", attrs={"type": "application/ld+json"})

                # Se obtienen los datos del json como un diccionario
                data = json.loads(script_tag.text)

                if "image" in data:
                    title.cover = data["image"]
                    title.save()

                if "description" in data:
                    title.description = data["description"]
                    title.save()

                if "alternateName" in data:
                    title.translatedtitle = data["alternateName"]
                    title.save()

            except Exception:
                pass

            # Cover: opción 2
            if title.cover == None:
                try:
                    img_tag = soup.find("img", class_="ipc-image")
                    img_src = img_tag["src"]
                    title.cover = simplify_url(img_src)
                    title.save()
                except Exception:
                    pass

            # Descripción: opción 2
            if title.description == None:
                try:
                    meta_description = soup.find("meta", attrs={"name": "description"})
                    content = meta_description["content"]
                    title.description = content
                    title.save()
                except Exception:
                    pass

        except Exception:
            pass

    # Se comprueba si es favorito o pendiente
    if user == None:
        is_favorite = None
        is_pending = None
        is_rated = None
        own_rating = None
    else:
        is_favorite = Favorites.objects.filter(userid=user, titleid=title).exists()
        is_pending = Pending.objects.filter(userid=user, titleid=title).exists()
        is_rated = Ratings.objects.filter(posterid=user, titleid=title).exists()
        if is_rated:
            user_rating = Ratings.objects.get(posterid=user, titleid=title)
            own_rating = {
                "comment": user_rating.comment,
                "addedDate": user_rating.addeddate,
                "rating": user_rating.rating,
                "username": user_rating.posterid.username,
                "avatarId": user_rating.posterid.avatarid.pk,
            }
        else:
            own_rating = None

    # Se comprueba que la descripción no sea el texto por defecto
    hashed_description = hashlib.md5(title.description.encode("utf-8")).hexdigest()
    if hashed_description == "03f874c3ad85cc7289dfd9e67009ff6e":
        description = "Sin datos"
    else:
        description = title.description

    # Se devuelve el diccionario
    return {
        "id": title.pk,
        "titleType": title_type,
        "primaryTitle": title.primarytitle,
        "originalTitle": title.originaltitle,
        "translatedTitle": title.translatedtitle,
        "startYear": title.startyear,
        "endYear": title.endyear,
        "runtimeMinutes": title.runtimeminutes,
        "language": title.language.rstrip(),
        "cover": title.cover,
        "description": description,
        "genres": genre_list,
        "crew": participant_list,
        "rating": rating_average["rating__avg"],
        "totalRatings": rating_count,
        "lastComments": last_comments,
        "isFavorite": is_favorite,
        "isPending": is_pending,
        "isRated": is_rated,
        "ownRating": own_rating,
    }


def get_new_token():
    # Genera un token aleatorio
    token_string = get_random_string(length=32)

    # Comprueba que el token no está en la BBDD
    while Tokens.objects.filter(token=token_string).exists():
        token_string = get_random_string(length=32)

    # Devuelve el token generado
    return token_string


def get_user(username, logged_user: Users = None, get_fav_pending: bool = False):
    # Devuelve datos de un usuario
    if isinstance(username, Users):
        user = username
    else:
        try:
            # Obtiene el usuario
            user = Users.objects.get(username=username)
        except ObjectDoesNotExist:
            # Si genera un error al obtener el usuario, devuelve none
            return None

    # Comprueba si el usuario loggeado es el mismo que el buscado
    if logged_user:
        user_matches = user.pk == logged_user.pk
    else:
        user_matches = False

    # Se obtienen todos los ratings
    user_ratings = Ratings.objects.filter(posterid=user)

    # Se obtienen todos los favoritos
    user_favorites = Favorites.objects.filter(userid=user).values("titleid")

    # Se obtienen los minutos
    total_minutes = Titles.objects.filter(pk__in=user_favorites).aggregate(
        Sum("runtimeminutes")
    )["runtimeminutes__sum"]

    # Se crea el diccionario de la respuesta
    result = {
        "isOwnUser": user_matches,
        "username": user.username,
        "birthdate": user.birthdate,
        "name": user.name,
        "surname": user.surname,
        "avatarId": user.avatarid.pk,
        "registerDate": user.registerdate,
        "isFollowed": None,
        "isFollower": None,
        "watchTime": total_minutes,
        "totalRatings": user_ratings.count(),
    }

    if user_matches:
        # Datos extra
        result["email"] = user.email
        result["phone"] = user.phone
    elif logged_user:
        # Es seguido
        result["isFollowed"] = Followers.objects.filter(
            followerid=logged_user, followedid=user
        ).exists()
        # Es seguidor
        result["isFollower"] = Followers.objects.filter(
            followedid=logged_user, followerid=user
        ).exists()

    # Número de seguidores y seguidos
    followers = Followers.objects.filter(followedid=user).count()
    result["followers"] = followers
    followed = Followers.objects.filter(followerid=user).count()
    result["following"] = followed

    if get_fav_pending:
        # Lista de favoritos
        favorites = Favorites.objects.filter(userid=user).order_by("-addeddate")
        favorites_list = []
        for favorite in favorites[0:5]:
            favorites_list.append(get_title(favorite.titleid.pk, logged_user))
        result["favorites"] = favorites_list

        # Lista de pendientes
        pendings = Pending.objects.filter(userid=user).order_by("-addeddate")
        pending_list = []
        for pending in pendings[0:5]:
            pending_list.append(get_title(pending.titleid.pk, logged_user))
        result["pending"] = pending_list

    return result
