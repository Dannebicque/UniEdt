from django.urls import path, include

urlpatterns = [
    path('', include("main.urls")),
    path('enseignants/', include("enseignants.urls")),
    path("events/", include("events.urls")),
    path('previsionnel/', include("previsionnel.urls")),
    path('programmation/', include("programmation.urls")),
]
