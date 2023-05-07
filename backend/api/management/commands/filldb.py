import contextlib
import json

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        p = 'data/'

        with contextlib.ExitStack() as stack:
            with stack.enter_context(open(f'{p}ingredients.json', 'r')) as f:
                ingredients = json.load(f)

            for ingredient in ingredients:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )