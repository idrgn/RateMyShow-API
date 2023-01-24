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
    # Funcionales
    path("admin/", admin.site.urls),
    path("titles/random", views.get_random_title),
    path("titles/<str:title_id>", views.get_title_by_id),
    path("users", views.register_user),
    path("sessions", views.sessions),
    # Hardcodeadas
    path("users/<str:username>", hardcoded.get_user_by_name),
    path("users/<str:username>/followers", hardcoded.get_follow_by_name),
    path("users/<str:username>/following", hardcoded.get_follow_by_name),
    path("users/<str:username>/ratings", hardcoded.get_ratings_by_name),
    path("users/<str:username>/follow", hardcoded.follow),
    path("users/feed", hardcoded.feed),
    path("users/best_rated", hardcoded.best_rated),
    path("users/recommendations", hardcoded.recommendations),
    path("users/latest", hardcoded.latest),
    path("users/favorites", hardcoded.favorites),
    path("users/pending", hardcoded.pending),
    path("titles/<str:title_id>/rating", hardcoded.rating),
    path("titles/<str:title_id>/pending", hardcoded.pending_by_id),
    path("titles/<str:title_id>/favorite", hardcoded.favorite_by_id),
]
