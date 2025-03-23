from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post, Category, Location)
class BlogAdmin(admin.ModelAdmin):
    pass
