from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            Shopping_carts, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartsSerializer, TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        user = self.request.user
        if is_in_shopping_cart == '1':
            return Recipe.objects.filter(shopping_carts__user=user)
        if is_favorited == '1':
            return Recipe.objects.filter(favorite__user=user)
        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            shopping_cart = Shopping_carts.objects.create(
                user=user,
                recipe=recipe,
            )
            serializer = ShoppingCartsSerializer(
                shopping_cart, context={"request": request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            Shopping_carts.objects.get(
                user=user,
                recipe=recipe,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        if Shopping_carts.objects.filter(user=user).exists():
            ingredients = IngredientsRecipe.objects.filter(
                recipe__shopping_carts__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(amount=Sum('amount'))

            with open('shopping_list.txt', 'w') as sh:
                sh.write('Список покупок:' + '\n')
                for ingr in ingredients:
                    sh.write(
                        ingr['ingredient__name'] + ' '
                        + str(ingr['amount']) + ' '
                        + ingr['ingredient__measurement_unit'] + '\n'
                    )
            response = FileResponse(
                open('shopping_list.txt', 'rb'), content_type='text/plain'
            )
            response['Content-Disposition'] = (
                'attachment;filename="shopping_list.txt"'
            )
            return response
        return Response(
            'Список покупок пуст.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            Favorite.objects.get(user=user, recipe=recipe)
        if request.method == 'POST':
            favorite = Favorite.objects.create(
                user=user,
                recipe=recipe,
            )
            serializer = FavoriteSerializer(
                favorite, context={"request": request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not Favorite.objects.filter(user=user).exists():
                return Response(
                    'Рецепт отсутсвует.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.get(
                user=user,
                recipe=recipe,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
