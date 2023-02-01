from django.contrib import admin
from django.urls import path
from webserviceapp import hardcoded, views

"""RateMyShow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


urlpatterns = [
    # Django
    path("admin/", admin.site.urls),
    # Públicas
    path("best", views.best_rated),
    path("latest", views.latest),
    # De usuario
    path("sessions", views.sessions),
    path("feed", views.get_feed),
    path("pending", views.get_pending),
    path("favorites", views.get_favorites),
    path("recommendations", views.recommendations),
    # Users
    path("users", views.search_register_user),
    path("users/<str:username>", views.get_user_by_name),
    path("users/<str:username>/followers", views.get_followers_by_name),
    path("users/<str:username>/following", views.get_following_by_name),
    path("users/<str:username>/ratings", hardcoded.get_ratings_by_name),
    path("users/<str:username>/follow", views.follow_user),
    # Títulos
    path("titles", views.title_search),
    path("titles/random", views.get_random_title),
    path("titles/<str:title_id>", views.get_title_by_id),
    path("titles/<str:title_id>/favorite", views.favorite_by_id),
    path("titles/<str:title_id>/pending", views.pending_by_id),
    path("titles/<str:title_id>/rating", views.rating),
    # Imágenes
    path("pfp/<str:name>", views.get_profile_picture),
    path("img/<str:name>", views.get_image),
]
