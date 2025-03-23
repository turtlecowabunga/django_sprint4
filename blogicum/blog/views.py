from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404


from .models import Comment, Category, Post
from .utils import get_publishable_posts, create_paginator
from .forms import ProfileEditForm, CreatePostForm, CreateCommentForm

User = get_user_model()


def index(request):
    template_name = 'blog/index.html'
    publishable_posts = get_publishable_posts()
    page_obj = create_paginator(request, publishable_posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        pk=post_id,
    )
    if (request.user == post.author
            or post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()):
        form = CreateCommentForm(request.POST or None)
        context = {
            'post': post,
            'comments': post.comments.all(),
            'form': form,
        }
        return render(request, template_name, context)
    else:
        raise Http404()


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments')).order_by(
        '-pub_date')
    page_obj = create_paginator(request, post_list)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    # При использовании annotate сортировка, указанная в
    # ordering мета-класса модели, не работает, поэтому
    # необходимо явно указывать order_by
    post_list = profile.posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = create_paginator(request, post_list)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


# Данный декторатор обеспечивает выполнение
# функции только залогиненным пользователям,
# если пользователь не залогинен, то происходит
# перенаправление на страницу логина, указанного в settings.LOGIN_URL,
# а в GET-параметре next передается текущий url
# для перенаправления после входа.
@login_required
def create_post(request):
    template_name = 'blog/create.html'
    user = request.user
    form = CreatePostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {'form': form}
    if form.is_valid():
        form.instance.author_id = user.id
        form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, template_name, context)


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'
    form = ProfileEditForm(request.POST or None, instance=request.user)
    context = {
        'form': form,
    }
    if form.is_valid():
        form.save()
    return render(request, template_name, context)


def edit_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    form = CreatePostForm(
        request.POST or None,
        request.FILES or None,
        instance=instance,
    )
    context = {'form': form}
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, template_name, context)


def delete_post(request, post_id):
    template_name = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CreatePostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    user = request.user
    get_object_or_404(Post, pk=post_id)
    Comment.objects.create(
        text=request.POST['text'],
        post_id=post_id,
        author_id=user.id,
    )
    return redirect('blog:post_detail', post_id=post_id)


def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    user = request.user
    instance = get_object_or_404(Comment,
                                 pk=comment_id)
    if instance.author != user:
        return redirect('blog:index')
    form = CreateCommentForm(
        request.POST or None,
        instance=instance,
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, template_name, context)
