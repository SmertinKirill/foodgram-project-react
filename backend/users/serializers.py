from rest_framework import serializers, validators
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import User, Follow


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


class FollowSerializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribe'
        )

    def get_is_subscribe(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated or request.user == obj:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()
