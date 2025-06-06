from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from recipes.models import Recipe
from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'recipes_count',
        'followers_count',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    @admin.display(description='Количество подписчиков')
    def followers_count(self, obj):
        return Follow.objects.filter(author=obj).count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
