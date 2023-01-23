import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Q
from bs4 import BeautifulSoup
from random import choice
import requests
import json

from .models import Titles, Users, Avatars, Tokens


def get_title_data(title_id):
    try:
        # Obtiene el título
        title = Titles.objects.get(id=title_id)
    except ObjectDoesNotExist:
        # Si genera un error al obtener el título, revuelve none
        return None

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

        # Se intenta hacer la petición
        try:
            request_response = requests.get(
                f"http://www.imdb.com/title/{title_id}/", headers=headers
            )
            soup = BeautifulSoup(request_response.text, "html.parser")

            # Se intenta obtener el cover
            try:
                img_tag = soup.find("img", class_="ipc-image")
                img_src = img_tag["src"]
                title.cover = img_src
                title.save()
            except Exception:
                pass

            # Se intenta obtener la descripción
            try:
                meta_description = soup.find("meta", attrs={"name": "description"})
                content = meta_description["content"]
                title.description = content
                title.save()
            except Exception:
                pass

        except Exception:
            pass

    # Se transforma el modelo a un diccionario
    return model_to_dict(title)


def get_title_by_id(r, title_id):
    # Obtiene el título
    try:
        response = get_title_data(title_id)
    except Exception:
        response = None

    # Si la respuesta es None, envía un status 404 (Not found)
    if response == None:
        return JsonResponse({"message": "Not found"}, status=404)

    # Se envía la respuesta con status 200 (OK)
    return JsonResponse(response, json_dumps_params={"ensure_ascii": False}, status=200)


def get_random_title(r):
    # Se obtienen todas las claves primarias de la tabla Titles
    pks = Titles.objects.values_list("pk", flat=True)

    # Se selecciona una de las claves
    random_pk = choice(pks)

    # Devuelve los datos
    return JsonResponse(
        get_title_data(random_pk),
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

        # Se intenta obtener el usuario de la BBDD con los datos obtenidos
        user_exists = Users.objects.filter(
            Q(username=data["username"])
            | Q(email=data["email"])
            | Q(phone=data["phone"])
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
        usuario = Users()
        usuario.username = data["username"]
        usuario.email = data["email"]
        usuario.phone = data["phone"]
        usuario.birthdate = data["birthDate"]
        usuario.name = data["name"]
        usuario.surname = data["surname"]

        # Se añade la fecha actual como fecha de registro
        usuario.registerdate = datetime.datetime.now()

        # Se obtienen todas las claves primarias de la tabla Avatars
        avatar_ids = Avatars.objects.values_list("pk", flat=True)

        # Se asigna un avatar aleatorio
        usuario.avatarid = Avatars.objects.get(pk=choice(avatar_ids))

        # Se asigna la contraseña encriptada
        usuario.set_password(data["password"])

        # Se guarda el usuario
        usuario.save()

        # Se genera el token
        token_string = get_random_string(length=32)
        new_token = Tokens()
        new_token.token = token_string
        new_token.userid = usuario
        new_token.save()

        # Se devuelve un 201
        return JsonResponse(
            {"sessionToken": token_string},
            json_dumps_params={"ensure_ascii": False},
            status=201,
        )
