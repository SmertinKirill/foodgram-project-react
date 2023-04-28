from rest_framework import viewsets
from .serializers import (IngredientSerializer, TagSerializer,
                          ShoppingCartsSerializer, RecipeSerializer,
                          FavoriteSerializer)
from recipes.models import (Ingredient, Tag, Recipe, Shopping_carts,
                            IngredientsRecipe, Favorite)
from .permissions import (IsAdminOrReadOnly,
                          IsAdminOrAuthorOrReadOnly, IsAuthenticated)
from .pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import FileResponse


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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_carts(self, request, pk):
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
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        if Shopping_carts.objects.filter(user=user).exists():
            ingredients = IngredientsRecipe.objects.filter(
                recipe__shopping_carts_recipe__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(amount=Sum('amount'))

            with open('shopping_list.txt', 'w') as sh:
                sh.write('Список покупок:' + '\n')
                for ingr in ingredients:
                    sh.write(
                        ingr['ingredient__name'] +
                        ' ' + str(ingr['amount']) +
                        ' ' + ingr['ingredient__measurement_unit'] + '\n'
                    )
            response = FileResponse('shopping_list.txt')
            return response
        return Response(
            'Список покупок пуст.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
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
