from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
from .models import Follow, User
from recipes.models import Recipe


class NewUserSerializer(UserSerializer):
    username = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )
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
            int(self.context.get('request').GET.get('recipes_limit'))
        )
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = RecipeForFollowsSerializer(recipes, many=True)
        return serializer.data
