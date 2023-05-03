from django.contrib import admin

from recipes.models import (Ingredient, IngredientsRecipe, Recipe,
                            Shopping_carts, Tag, TagsRecipe)

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientsRecipe)
admin.site.register(TagsRecipe)
admin.site.register(Shopping_carts)
