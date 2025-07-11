from django.urls import path
from . import views

app_name = "programmation"

urlpatterns = [
    path("", views.index, name="index"),
    path("import_previsionnel/", views.import_previsionnel, name="import_previsionnel"),
    path('partie1/', views.partie1, name='partie1'),
    path('update/', views.update_programmation, name='update_programmation'),
    path('update_all/', views.update_all, name='update_all'),
    path('etudiants_1/', views.etudiants_1, name='etudiants_1'),
    path('profs_1/', views.profs_1, name='profs_1'),
    path('export_semaines/', views.export_semaines_view, name='export_semaines'),
]
