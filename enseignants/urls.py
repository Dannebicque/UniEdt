from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste_enseignants, name="liste_enseignants"),
    path("ajouter/", views.ajouter_enseignant, name="ajouter_enseignant"),
    path("modifier/<str:code>/", views.modifier_enseignant, name="modifier_enseignant"),
    path("supprimer/<str:code>/", views.confirmer_suppression_enseignant, name="supprimer_enseignant"),
    path("contraintes/<str:code>/", views.contraintes_enseignant, name="contraintes_enseignant"),
    path("contraintes/<str:code>/supprimer/<int:index>/", views.supprimer_contrainte, name="supprimer_contrainte"),
    path("contraintes/<str:code>/modifier/<int:index>/", views.modifier_contrainte, name="modifier_contrainte"),
]
