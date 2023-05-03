from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views

app_name = 'users'

v1_router = DefaultRouter()

v1_router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
