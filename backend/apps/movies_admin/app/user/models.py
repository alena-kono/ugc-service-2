from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class MoviesUserManager(BaseUserManager):
    def create_user(
        self,
        user_id: str,
        username: str,
        password: str | None = None,
        first_name: str = None,
        last_name: str = None,
    ):
        if not (username and user_id):
            raise ValueError("Users must have username and id")

        user = self.model(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_staff=True,
            is_admin=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password=password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=True)

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    USERNAME_FIELD = "username"

    objects = MoviesUserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self) -> str:
        return f"{self.username} {self.id}"
