from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import views

v1_router = DefaultRouter()

v1_router.register('ingredients',
                   views.IngredientViewSet,
                   basename='ingredients')
v1_router.register('tags', views.TagViewSet, basename='tags')
v1_router.register('recipes', views.RecipeViewSet, basename='recipes')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    views.RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('', include(v1_router.urls)),
]
