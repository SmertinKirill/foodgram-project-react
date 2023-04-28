from rest_framework import viewsets
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from recipes.models import Ingredient, Tag, Recipe
from .permissions import (IsAdminOrReadOnly,
                          IsAdminOrAuthorOrReadOnly)
from .pagination import CustomPagination
# from rest_framework.response import Response
# from rest_framework import status


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
