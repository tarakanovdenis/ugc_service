import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email,
        password=None,
        first_name=None,
        last_name=None
    ):
        if not username:
            raise ValueError('Enter an username name.')

        if not email:
            raise ValueError('Enter an email.')

        if not first_name:
            raise ValueError('Enter a first name.')

        if not last_name:
            raise ValueError('Enter a last name.')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        email,
        password=None,
        first_name=None,
        last_name=None
    ):
        user = self.create_user(
            username,
            email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_subscriber = True
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField('username', max_length=32, unique=True)
    email = models.EmailField('email', max_length=32, unique=True)
    password = models.CharField('password', max_length=128)
    first_name = models.CharField('first name', max_length=32)
    last_name = models.CharField('last name', max_length=32)
    is_superuser = models.BooleanField(
        ('superuser status'),
        default=False,
        help_text=(
            'Designates whether the user is superuser.'
        )
    )
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=(
            'Designates whether the user is allowed to access the admin site.'
        )
    )
    is_active = models.BooleanField(
        ('active status'),
        default=True,
        help_text=(
            'Designates whether the user is active.'
        )
    )
    is_subcriber = models.BooleanField(
        ('subscriber status'),
        default=False,
        help_text=(
            'Designates whether the user is subscriber'
        ),
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # строка с именем поля модели, которая используется в качестве уникального
    # идентификатора
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        # 'username',
        'email',
        'password',
        'first_name',
        'last_name',
    ]

    # менеджер модели
    objects = MyUserManager()

    def __str__(self):
        return (
            f'User(id={self.id}, username={self.username}, email={self.email}, '
            f'first_name={self.first_name}, last_name={self.last_name})'
        )

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
