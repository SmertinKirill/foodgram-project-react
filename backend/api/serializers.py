import base64

from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            Shopping_carts, Tag)
from rest_framework import serializers
from users.serializers import NewUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientWithAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientWithAmountCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = NewUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = IngredientWithAmountSerializer(
        source='ingredients_recipe',
        many=True
    )
    tags = TagSerializer(many=True, read_only=True)
    cooking_time = serializers.IntegerField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'author', 'image', 'name',
            'is_favorited', 'is_in_shopping_cart', 'text', 'cooking_time'
        )
    read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Recipe.objects.filter(favorite__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.shopping_carts.filter(recipe=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = NewUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = IngredientWithAmountCreateSerializer(
        source='ingredients_recipe',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'author', 'image', 'name', 'text', 'cooking_time',
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_recipe')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            print('!!!', ingredient_data)
            ingredient_id = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']
            IngredientsRecipe.objects.create(
                recipe=recipe, ingredient_id=ingredient_id, amount=amount)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.ingredients.clear()
        if 'ingredients_recipe' in validated_data:
            ingredients_data = validated_data.pop('ingredients_recipe')
            updates = []
            for ingredient in ingredients_data:
                cur_ingr, status = IngredientsRecipe.objects.get_or_create(
                    recipe_id=instance.id,
                    ingredient_id=ingredient['ingredient']['id'],
                    amount=ingredient['amount']
                )
                updates.append(cur_ingr)
            instance.ingredients_recipe.set(updates)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.save()
        return instance


class ShoppingCartsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='recipe.id',)
    name = serializers.CharField(read_only=True, source='recipe.name')
    image = serializers.CharField(read_only=True, source='recipe.image',)
    cooking_time = serializers.IntegerField(
        read_only=True, source='recipe.cooking_time',
    )

    class Meta:
        model = Shopping_carts
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(ShoppingCartsSerializer):
    class Meta(ShoppingCartsSerializer.Meta):
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
