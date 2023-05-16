import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class AdCategory(models.Model):
    ad = models.ForeignKey('Advertisement', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category.name


class Advertisement(models.Model):
    title = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through=AdCategory)
    text = models.TextField(default='')

    def __str__(self):
        return f'{self.id}-{self.title[:30]}'

    def get_absolute_url(self):
        return f'/{self.id}'


def get_upload_path(instasnce, filename):
    path = os.path.join(settings.BASE_DIR, 'media', 'content', str(instasnce.ad.id))
    if not os.path.exists(path):
        os.mkdir(path)
    return f'content/{instasnce.ad.id}/{filename}'


class AdFiles(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_path)

    def __str__(self):
        return f'{self.file.name}'


class Reply(models.Model):
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    text = models.TextField()
    accepted = models.IntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])

    def __str__(self):
        return f'{self.text[:50]}'


class Profile(AbstractUser):
    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)


class OneTimeCode(models.Model):
    code = models.PositiveIntegerField(validators=[MaxValueValidator(9999)])
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)