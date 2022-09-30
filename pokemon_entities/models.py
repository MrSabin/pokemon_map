from django.db import models  # noqa F401
from django.utils import timezone


class Pokemon(models.Model):
    title_ru = models.CharField(max_length=200, verbose_name="Название (RU)")
    title_en = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Название (EN)"
    )
    title_jp = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Название (JP)"
    )
    photo = models.ImageField(
        upload_to="pokemons", null=True, blank=True, verbose_name="Изображение"
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="Описание")
    previous_evolution = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="next_evolutions",
        null=True,
        blank=True,
        verbose_name="Предыдущая эволюция",
    )

    def __str__(self):
        return self.title_ru


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        verbose_name="Тип покемона",
        related_name="entities",
    )
    lat = models.FloatField(verbose_name="Широта")
    lon = models.FloatField(verbose_name="Долгота")
    appeared_at = models.DateTimeField(
        default=timezone.now, verbose_name="Время появления"
    )
    disappeared_at = models.DateTimeField(
        default=timezone.now, verbose_name="Время исчезновения"
    )
    level = models.IntegerField(null=True, blank=True, verbose_name="Уровень")
    health = models.IntegerField(
        null=True, blank=True, verbose_name="Здоровье")
    strength = models.IntegerField(null=True, blank=True, verbose_name="Сила")
    defence = models.IntegerField(null=True, blank=True, verbose_name="Защита")
    stamina = models.IntegerField(
        null=True, blank=True, verbose_name="Выносливость")

    def __str__(self):
        return f"{self.pokemon.title_ru} lvl {self.level}"
