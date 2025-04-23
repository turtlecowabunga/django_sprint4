from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Post, Category, Location, Comment)
class BlogAdmin(admin.ModelAdmin):
    pass
