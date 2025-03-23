from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post


def get_publishable_posts():
    posts = Post.objects.select_related(
        "category",
        "author",
        "location"
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )
    return posts


def create_paginator(request, post_list):
    """Создает пагинатор и возвращает страницу с номером из GET запроса."""
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return page_obj
