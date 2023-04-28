from django.contrib import admin
from recipes.models import (Ingredient, Tag, Recipe, IngredientsRecipe,
                            TagsRecipe, Shopping_carts)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientsRecipe)
admin.site.register(TagsRecipe)
admin.site.register(Shopping_carts)
