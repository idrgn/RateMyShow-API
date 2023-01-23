from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from bs4 import BeautifulSoup
from random import choice
import requests

from .models import Titles


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

    # Se obtiene el objeto asociado a esa tabla
    random_item = Titles.objects.get(pk=random_pk)

    # Devuelve los datos
    return JsonResponse(
        get_title_data(random_item.id),
        json_dumps_params={"ensure_ascii": False},
        status=200,
    )


@csrf_exempt
def register_user(r):
    if r.method == "POST":
        return JsonResponse(
            {"sessionToken": "ABCDEF123456789"},
            json_dumps_params={"ensure_ascii": False},
            status=201,
        )
