from django.forms.models import model_to_dict
from django.http import JsonResponse

from .models import Titles

def get_title_by_id(r, title_id):
    # Obtiene el título
    title = Titles.objects.get(id=title_id)

    # Se transforma el modelo a un diccionario
    response = model_to_dict(title)

    # Se envía la respuesta
    return JsonResponse(
        response,
        json_dumps_params={"ensure_ascii": False},
    )
