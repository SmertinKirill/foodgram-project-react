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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        fieldsets += (('Количество добавлений в избранное', {'fields': ('favorites_count',)}),)
        return fieldsets


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsRecipe)
admin.site.register(TagsRecipe)
admin.site.register(Shopping_carts)
