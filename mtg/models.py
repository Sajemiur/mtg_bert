from django.db import models


class Color(models.Model):
    name = models.CharField(primary_key=True, max_length=1)


class Subtype(models.Model):
    name = models.CharField(primary_key=True, max_length=16)


class Supertype(models.Model):
    name = models.CharField(primary_key=True, max_length=16)


class Type(models.Model):
    name = models.CharField(primary_key=True, max_length=16)


class Card(models.Model):
    name = models.CharField(primary_key=True, max_length=32)
    colors = models.ManyToManyField(Color)
    cmc = models.IntegerField(default=0)
    manaCost = models.CharField(max_length=32)
    subtypes = models.ManyToManyField(Subtype)
    supertypes = models.ManyToManyField(Supertype)
    text = models.CharField(max_length=256)
    types = models.ManyToManyField(Type)
    power = models.CharField(max_length=3)
    toughness = models.CharField(max_length=3)
    img = models.URLField()

    def __str__(self):
        return self.name

    @staticmethod
    def query_attributes():
        return {'name': 'name__contains', 'colors': 'colors__name__iexact', 'cmc': 'cmc', 'manaCost': 'name__iexact',
                'subtypes': 'subtypes__name__iexact', 'supertypes': 'supertypes__name__iexact', 'text': 'text__contains',
                'types': 'types__name__iexact', 'power': 'power', 'toughness': 'toughness'}.items()
