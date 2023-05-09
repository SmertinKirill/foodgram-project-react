from django.contrib import admin
from recipes.models import (Ingredient, IngredientsRecipe, Recipe,
                            Shopping_carts, Tag, TagsRecipe)


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name')


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('name', 'author', 'tags')
    list_display = ('name', 'author', 'favorites_count')

    def favorites_count(self, obj):
        return obj.favorite.count()

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        if obj is None:
            return fields
        fields += ('favorites_count',)
        return fields


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsRecipe)
admin.site.register(TagsRecipe)
admin.site.register(Shopping_carts)
