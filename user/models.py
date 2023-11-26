from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from user.managers import CustomUserManager


class UserRole(Enum):
    CITIZEN = 1

    MUNICIPALITY_WORKER = 90
    MUNICIPALITY_ADMIN = 100

    MODERATOR = 555
    ADMIN = 777


class Photo(models.Model):
    image = models.ImageField(upload_to='static/photos/', unique=True)


class City(models.Model):
    region = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    timezone = models.IntegerField(default=3)
    logo = models.ImageField(upload_to='static/city_logo/', default='static/city_logo/default.png')

    def __str__(self):
        return f'{self.region}, {self.name}'


class Municipality(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255)
    creation_date = models.DateField()

    logo = models.ImageField(upload_to='static/municipality_logo/', default='static/municipality/default.png')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    SEX_CHOICES = [
        ('M', 'Мужчина'),
        ('F', 'Женщина')
    ]

    name = models.CharField('Имя', max_length=255)
    surname = models.CharField('Фамилия', max_length=255)
    patronymic = models.CharField('Отчество', max_length=255, null=True)
    username = models.EmailField(unique=True, verbose_name='Email', blank=False)
    sex = models.CharField(choices=SEX_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True)
    phone = models.CharField(null=True, unique=True)
    role = models.IntegerField(default=1)
    address_street = models.CharField(max_length=255)
    address_house = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='static/user_logo/', default='static/user_logo/default.png', null=True)
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user is an admin.')
    is_superuser = models.BooleanField(default=False, help_text='Designates whether the user is an admin.')
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)

    REQUIRED_FIELDS = ['name', 'surname', 'address_street', 'address_house', 'city']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class Position(models.Model):
    name = models.CharField(max_length=255)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class News(models.Model):
    class NewsCategory(models.TextChoices):
        WATER = 'Вода'
        LIGHT = 'Освещение'
        GAS = 'Газ'
        HEATING = 'Отопление'
        REPAIR_WORK = 'Ремонтные работы'
        MSW_REMOVAL = 'Вывоз ТКО'
        STREET = 'Улица'
        ACCUMULATION_SITES_CONDITION = 'Состояние мест накопления'
        OTHER = 'Иное'

    city = models.ForeignKey(City, on_delete=models.CASCADE, default=1)
    category = models.CharField(choices=NewsCategory.choices, default=NewsCategory.OTHER)
    title = models.CharField(max_length=100)
    short_description = models.TextField(max_length=210)
    text = models.TextField()
    photos = models.ManyToManyField(Photo, blank=True)
    publication_date = models.DateTimeField(default=timezone.now)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.title


class Appeal(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    photos = models.ManyToManyField(Photo, blank=True)
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class AppealAnswer(models.Model):
    appeal = models.OneToOneField(Appeal, on_delete=models.CASCADE, related_name='answer', null=True)
    answerer = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class Notification(models.Model):
    appeal_answer = models.ForeignKey(AppealAnswer, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    question_text = models.TextField(max_length=True)

    def __str__(self):
        return self.title


class Choice(models.Model):
    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(default=timezone.now)
