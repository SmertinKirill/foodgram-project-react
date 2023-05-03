from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.permissions import IsAuthenticated

from .models import Follow, User
from .serializers import FollowSerializer, NewUserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = NewUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination,
    )
    def subscriptions(self, request, pk=None):
        user = request.user
        follows = Follow.objects.filter(user=user)
        authors = [follow.author for follow in follows]
        serializer = FollowSerializer(
            authors, many=True, context={"request": request}
        )
        paginated_data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(paginated_data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        print('!!! ', request.__dict__)
        if request.method == 'DELETE':
            Follow.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                'Вы уже подписаны на данного пользователя!',
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user == author:
            return Response(
                'Подписка на себя невозможна!',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            author=author,
        )
        serializer = FollowSerializer(
            author, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
