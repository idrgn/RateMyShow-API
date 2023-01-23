import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.utils.crypto import get_random_string

from .models import Titles, Tokens, Genres, Genretypes


"""Funciones de BBDD de RateMyShow

Funciones de ayuda encargadas de obtener datos de la BBDD que se usarían en varias vistas

Métodos:
 - get_title: obtiene los datos procesados de un título
 - get_new_token: obtiene un token de sesión de usuario no existente en la BBDD
"""


def get_title(title_id):
    try:
        # Obtiene el título
        title = Titles.objects.get(id=title_id)
    except ObjectDoesNotExist:
        # Si genera un error al obtener el título, revuelve none
        return None

    # Se obtienen los géneros
    genres = Genres.objects.filter(titleid=title_id)

    # Se añaden a una lista
    genre_list = []
    for genre in genres:
        genre_list.append(genre.genreid.genre)

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
    title_dict = model_to_dict(title)

    # Se añaden los campos extra
    title_dict["genres"] = genre_list

    # Se devuelve el diccionario
    return title_dict


def get_new_token():
    # Genera un token aleatorio
    token_string = get_random_string(length=32)

    # Comprueba que el token no está en la BBDD
    while Tokens.objects.filter(token=token_string).exists():
        token_string = get_random_string(length=32)

    # Devuelve el token generado
    return token_string
