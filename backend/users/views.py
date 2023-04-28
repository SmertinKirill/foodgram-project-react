from .models import User, Follow
from .serializers import NewUserSerializer, FollowSerializer
from djoser.views import UserViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from api.pagination import CustomPagination


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = NewUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get'],
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

    # @action(
    #     detail=True,
    #     methods=['delete'],
    #     url_name='subscribe',
    # )
    # def unsubscribe(self, request, id):
    #     print('DDD')
    #     author = get_object_or_404(User, id=id)
    #     if not Follow.objects.filter(user=request.user,
    #                                  author=author).exists():
    #         return Response(
    #             'Вы не подписаны на данного пользователя!',
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     if request.user == author:
    #         return Response(
    #             'Отписаться от себя невозможно!',
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     Follow.objects.get(user=request.user, author=author).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
