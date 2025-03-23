from django import forms
from django.forms import models


from .models import Comment, User, Post


class ProfileEditForm(models.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class CreatePostForm(models.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location',
                  'image', 'pub_date',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CreateCommentForm(models.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': '40', 'rows': '5'})
        }
