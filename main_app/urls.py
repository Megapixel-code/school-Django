from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", views.safe_get_maison_link, name="home2"),
    path("profil/", views.profil, name="profil"),
    path("deconnexion/", views.logout_user, name="deconnexion"),
    path("connexion/", views.login_user, name="connexion"),
    path("incription/", views.register_user, name="inscription"),
    path("objets/", views.objets, name="main"),
    path("objets/ajouter_objet/<str:piece_id>/", views.add_objet, name="ajouter_objet"),
    path("objets/ajouter_piece/", views.add_piece, name="ajouter_piece"),
    path("maison/", views.maison, name="maison"),
    path("maison/cree/", views.create_maison, name="cree_maison"),
    path("maison/rejoindre/", views.join_maison, name="rejoindre_maison"),
]