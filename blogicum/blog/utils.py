from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post


def get_publishable_posts(category=None, author=None):
    posts = Post.objects.select_related(
        "category",
        "author",
        "location"
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )
    if category:
        posts = posts.filter(category=category)
    if author:
        posts = posts.filter(author=author)
    else:
        posts = posts.filter(
            category__is_published=True,
            pub_date__lte=timezone.now(),
            is_published=True
        )
    return posts


def create_paginator(request, post_list):
    """Создает пагинатор и возвращает страницу с номером из GET запроса."""
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return page_obj
