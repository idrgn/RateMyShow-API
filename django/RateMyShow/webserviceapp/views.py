import datetime
import json
from random import choice

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .database import get_new_token, get_title
from .models import Avatars, Favorites, Followers, Pending, Titles, Tokens, Users

"""Vistas de RateMyShow"""


def title_search(r):
    if r.method == "GET":
        # Se obtienen los parámetros de URL
        query = r.GET.get("query", None)

        # Si no se envía query, devuelve un 404
        if query == None:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se obtiene la página actual
        page = r.GET.get("page", 0)

        # Si es string, intenta convertirla a número
        if isinstance(page, str):
            try:
                page = int(page)
            except Exception:
                page = 0

        # Se obtienen los resultados
        search = Titles.objects.filter(
            Q(primarytitle__icontains=query) | Q(originaltitle__icontains=query)
        )

        # Cantidad de resultados por página
        amount_per_page = 15

        # Se almacenan los datos de cada título en una lista
        result_list = []
        for title in search[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list.append(get_title(title.id))

        # Se devuelve la lista
        return JsonResponse(
            result_list,
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def best_rated(r):
    if r.method == "GET":
        # Se obtiene la página actual
        page = r.GET.get("page", 0)

        # Si es string, intenta convertirla a número
        if isinstance(page, str):
            try:
                page = int(page)
            except Exception:
                page = 0

        # Se obtienen los resultados
        titles = (
            Titles.objects.prefetch_related("ratings_set")
            .annotate(average_rating=Avg("ratings__rating"))
            .order_by("-average_rating")
        )

        # Cantidad de resultados por página
        amount_per_page = 15

        # Se almacenan los datos de cada título en una lista
        result_list = []
        for title in titles[amount_per_page * page : amount_per_page * (page + 1)]:
            result_list.append(get_title(title.id))

        # Se devuelve la lista
        return JsonResponse(
            result_list,
            json_dumps_params={"ensure_ascii": False},
            status=200,
            safe=False,
        )


def get_title_by_id(r, title_id):
    if r.method == "GET":
        # Obtiene el título
        try:
            response = get_title(title_id)
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
            get_title(random_pk),
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


@csrf_exempt
def register_user(r):
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
            return JsonResponse({"message": "Not found"}, status=400)

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
            return JsonResponse({"message": "Not found"}, status=400)

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
            return JsonResponse({"message": "Not found"}, status=400)

        # Devuelve los datos del usuario2
        return JsonResponse(
            get_title(model_to_dict(token.userid)),
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


def get_user_by_name(r, username):
    if r.method == "GET":
        # Se intenta obtener el SessionToken de los headers
        try:
            sesion_token = r.headers["SessionToken"]
        except Exception:
            # sesion_token = ""
            return JsonResponse({"message": "Unauthorized"}, status=401)

        # Intenta buscar el usuario en la BBDD
        try:
            user = Users.objects.get(username=username)
        except Exception:
            return JsonResponse({"message": "Not found"}, status=404)

        # Se comprueba que es el propio usuario
        user_matches = Tokens.objects.filter(
            Q(token=sesion_token) & Q(userid=user.id)
        ).exists()

        # Se crea el diccionario
        user_dict = {
            "isOwnUser": user_matches,
            "username": user.username,
            "birthdate": user.birthdate,
            "name": user.name,
            "surname": user.surname,
            "avatarId": user.avatarid.pk,
            "registerDate": user.registerdate,
        }

        # Si es el propio usuario se añaden datos extra.
        if user_matches:
            user_dict["email"] = user.email
            user_dict["phone"] = user.phone

        # Número de seguidores y seguidos
        followers = Followers.objects.filter(followedid=user).count()
        user_dict["followers"] = followers

        followed = Followers.objects.filter(followerid=user).count()
        user_dict["following"] = followed

        # Lista de favoritos
        favorites = Favorites.objects.filter(userid=user).order_by("-addeddate")
        favorites_list = []
        for favorite in favorites[0:5]:
            favorites_list.append(get_title(favorite.titleid.pk))
        user_dict["favorites"] = favorites_list

        # Lista de pendientes
        pendings = Pending.objects.filter(userid=user).order_by("-addeddate")
        pending_list = []
        for pending in pendings[0:5]:
            pending_list.append(get_title(pending.titleid.pk))
        user_dict["pending"] = pending_list

        return JsonResponse(
            user_dict,
            json_dumps_params={"ensure_ascii": False},
            status=200,
        )


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

        # Añade titulo a favoritos
        favorite = Favorites()
        favorite.userid = token.userid
        favorite.titleid = Titles.objects.get(pk=title_id)
        favorite.addeddate = datetime.date.today()
        favorite.save()
        return JsonResponse({"message": "OK"}, status=200)
