from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (USER, 'Аутентифицированный пользователь'),
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=USER_ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return (self.role == User.ADMIN) or self.is_staff

    @property
    def is_user(self):
        return self.role == User.USER

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_following'
            )
        ]
