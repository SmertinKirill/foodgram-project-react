from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers, validators

from .models import Follow, User


class NewUserSerializer(UserSerializer):
    is_subscribe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribe'
        )
        model = User

    def get_is_subscribe(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated or request.user == obj:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class NewUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            lookup='iexact',
            message='Пользователь с таким username уже сущестует'
        )]
    )
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all(),
            lookup='iexact',
            message='Пользователь с таким email уже сущестует'
        )]
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class RecipeForFollowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribe', 'recipes'
        )

    def get_is_subscribe(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated or request.user == obj:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        recipes_limit = (
            int(self.context.get('request').GET.get('recipes_limit', 7))
        )
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = RecipeForFollowsSerializer(recipes, many=True)
        return serializer.data


class FollowValidateSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()

    def validate_author_id(self, value):
        request = self.context.get('request')
        author = get_object_or_404(User, id=value)
        if request.user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Follow.objects.filter(user=request.user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя'
            )
        return author.id

    def create(self, validated_data):
        author_id = validated_data['author_id']
        return Follow.objects.create(
            user=self.context['request'].user,
            author_id=author_id
        )
