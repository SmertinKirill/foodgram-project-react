from api.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import (FollowSerializer, FollowValidateSerializer,
                          NewUserSerializer)


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
        authors = User.objects.filter(following__user=user)
        serializer = FollowSerializer(
            authors, many=True, context={"request": request}
        )
        paginated_data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(paginated_data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowValidateSerializer,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'DELETE':
            Follow.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(
            data={"author_id": id},
            context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        serializer = FollowSerializer(
            author, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
