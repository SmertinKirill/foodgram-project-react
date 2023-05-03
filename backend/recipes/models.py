from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .validators import color_regex


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Tag name',
        blank=False,
        null=False
    )
    color = models.CharField(
        max_length=7,
        validators=[color_regex],
        blank=False,
        null=False,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=512,
        verbose_name='Ingredient name',
        blank=False,
        null=False,
    )
    measurement_unit = models.CharField(max_length=32)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингердиент'
        verbose_name_plural = 'Ингердиенты'


class Recipe(models.Model):
    name = models.CharField(max_length=256, verbose_name='Recipe name')
    text = models.TextField(
        'Описание',
        max_length=10000,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='media/recipes/images/',
        null=False,
    )
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipe',
        related_name='recipes',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsRecipe',
        related_name='recipes',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_recipe',
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
    )


class TagsRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class Shopping_carts(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
