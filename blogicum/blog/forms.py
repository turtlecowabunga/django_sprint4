from django import forms
from django.forms import models


from .models import Comment, Post


class PostForm(models.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location',
                  'image', 'pub_date', 'is_published')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(models.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': '40', 'rows': '5'})
        }
