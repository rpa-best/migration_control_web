from django.contrib import admin
from django.contrib.auth import get_user_model
from ..models.news import News, Tags, TagsNew

User = get_user_model()


class TagsNewInline(admin.TabularInline):
    model = TagsNew
    extra = 1


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'date_publication', 'author']
    inlines = [TagsNewInline]

    # def save_model(self, request, obj, form, change):
    #     if not obj.author:
    #         # Автоматическое заполнение автора (авторизованного пользователя)
    #         obj.author = request.user
    #     super().save_model(request, obj, form, change)

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)