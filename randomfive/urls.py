from django.urls import path
from randomfive import views

urlpatterns = [
        path('auth/', views.auth),
        path('', views.showfriends),
        path('logout/', views.delete_cookie),
]
