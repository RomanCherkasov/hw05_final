from .models import Post, Comment
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text',
                  'group',
                  'image', ]
        labels = {'text': 'Текст статьи',
                  'group': 'Группа', }
        help_texts = {'text': 'Введите текст статьи',
                      'group': 'Выберите группу', }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = {'text', }
