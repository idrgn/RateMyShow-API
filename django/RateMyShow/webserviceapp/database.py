import json

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
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
"""


def simplify_url(url):
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
    for rating in all_ratings.order_by("-addeddate")[0:10]:
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
        isFavorite = None
        isPending = None
        isRated = None
    else:
        isFavorite = Favorites.objects.filter(userid=user, titleid=title).exists()
        isPending = Pending.objects.filter(userid=user, titleid=title).exists()
        isRated = Ratings.objects.filter(posterid=user, titleid=title).exists()

    # Se devuelve el diccionario
    return {
        "id": title.pk,
        "titleType": title_type,
        "primaryTitle": title.primarytitle,
        "originalTitle": title.originaltitle,
        "startYear": title.startyear,
        "endYear": title.endyear,
        "runtimeMinutes": title.runtimeminutes,
        "language": title.language.rstrip(),
        "cover": title.cover,
        "description": title.description,
        "genres": genre_list,
        "crew": participant_list,
        "rating": rating_average["rating__avg"],
        "totalRatings": rating_count,
        "lastComments": last_comments,
        "isFavorite": isFavorite,
        "isPending": isPending,
        "isRated": isRated,
    }


def get_new_token():
    # Genera un token aleatorio
    token_string = get_random_string(length=32)

    # Comprueba que el token no está en la BBDD
    while Tokens.objects.filter(token=token_string).exists():
        token_string = get_random_string(length=32)

    # Devuelve el token generado
    return token_string


def get_user(username, logged_user: Users = None):
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
    user_matches = user.pk == logged_user.pk

    # Se crea el diccionario de la respuesta
    result = {
        "isOwnUser": user_matches,
        "username": user.username,
        "birthdate": user.birthdate,
        "name": user.name,
        "surname": user.surname,
        "avatarId": user.avatarid.pk,
        "registerDate": user.registerdate,
    }

    if user_matches:
        # Datos personales
        result["email"] = user.email
        result["phone"] = user.phone
        # Es seguido / seguidor
        result["isFollowed"] = None
        result["isFollower"] = None
    else:
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
