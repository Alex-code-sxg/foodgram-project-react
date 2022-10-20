from django.contrib.auth.models import AbstractUser
from django.db import models


ADMIN = 'admin'
USER = 'user'
GUEST = 'guest'


class User(AbstractUser):
    USER_ROLES = [
        (ADMIN, ADMIN),
        (USER, USER),
        (GUEST, GUEST),
    ]
    email = models.EmailField(
        'Электронная почта',
        help_text='Электронная почта пользователя',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        'Имя пользователя',
        help_text='Имя пользователя',
        max_length=150,
        unique=False
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        help_text='Фамилия пользователя',
        max_length=150,
        unique=False
    )
    password = models.CharField(
        'Пароль',
        help_text='Пароль',
        max_length=150,
    )
    role = models.CharField(
        'Роль',
        help_text='Роль пользователя',
        max_length=150,
        choices=USER_ROLES,
        default='user',
    )

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_guest(self):
        return self.role == GUEST

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def str(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription_user_author'
            )
        ]
