from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import (CreateView, DetailView,
                                  DeleteView, ListView, UpdateView)
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

from .models import Comment, Category, Post
from .utils import get_publishable_posts, create_paginator
from .forms import PostForm, CommentForm

User = get_user_model()


class AuthorRequiredMixin():
    """Проверяет является текущий пользователь автором экземпляра модели,
    если нет, то перенаправляет на URL объекта.
    Работает с UpdateView, DeleteView.
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.author:
            return redirect(self.object)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.author:
            return redirect(self.object)
        return super().post(request, *args, **kwargs)


class IndexListView(ListView):
    template_name = 'blog/index.html'
    queryset = get_publishable_posts()
    paginate_by = 10


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    model = Post
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        # Либо текущий пользователь - автор поста и может посмотреть пост,
        # либо  пост публикуемый, категория публикуемая и дата публикации
        # не будущая, тогда любой пользователь может посмотреть пост,
        #  иначе - ошибка 404
        if (self.request.user == post.author
                or post.is_published
                and post.category.is_published
                and post.pub_date <= timezone.now()):
            context['comments'] = post.comments.all()
            context['form'] = CommentForm()
            return context
        else:
            raise Http404()


class CategoryPostsListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10
    ordering = ('-pub_date',)

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get('category_slug'),
            is_published=True,
        )
        self.queryset = get_publishable_posts(category=self.category)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileDetailView(DetailView):
    template_name = 'blog/profile.html'
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = context['profile']
        post_list = get_publishable_posts(author=profile)
        context['page_obj'] = create_paginator(self.request, post_list)
        return context


# LoginRequiredMixin аналогичен @login_required только для CBV
class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        self.success_url = reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )
        return super().get_success_url()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email',)
    model = User

    def get_object(self, queryset=None):
        self.kwargs['pk'] = self.request.user.id
        return super().get_object(queryset)

    def get_success_url(self):
        self.success_url = reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username},
        )
        return super().get_success_url()


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    template_name = 'blog/create.html'
    form_class = PostForm
    model = Post
    pk_url_kwarg = 'post_id'


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=context['post'])
        return context


class CommentAddRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = 'blog:post_detail'

    def get(self, request, *args, **kwargs):
        # Существует ли пост с таким id, если нет, ошибка 404
        self.post_instance = get_object_or_404(
            Post, pk=self.kwargs.get('post_id')
        )
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = CommentForm(
                data={'text': self.request.POST['text']}
            )
            if form.is_valid():
                form.instance.post = self.post_instance
                form.instance.author = self.request.user
                form.save()
        return super().get_redirect_url(*args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    template_name = 'blog/comment.html'
    context_object_name = 'comment'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        self.success_url = reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')},
        )
        return super().get_success_url()

    def get(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return super().get(request, *args, **kwargs)
