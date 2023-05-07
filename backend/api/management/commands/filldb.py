import contextlib
import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        p = 'data/'

        with contextlib.ExitStack() as stack:
            ingredients = csv.DictReader(
                stack.enter_context(open(f'{p}ingredients.csv', 'r'))
            )

            for row in ingredients:
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
