from django.forms.models import model_to_dict
from django.http import JsonResponse
from bs4 import BeautifulSoup

from .models import Titles

import requests


def get_title_by_id(r, title_id):
    # Obtiene el título
    title = Titles.objects.get(id=title_id)

    # Si los datos adicionales no existen en la BBDD obtienen de la web
    if title.cover == None or title.description == None:

        # Se definen headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
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
    response = model_to_dict(title)

    # Se envía la respuesta
    return JsonResponse(
        response,
        json_dumps_params={"ensure_ascii": False},
    )
