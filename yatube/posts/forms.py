from django import forms

from .models import Post, Comment , Follow


class PostForm (forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = ('Введите текст')
        self.fields['group'].empty_label = ('Введите название группы')

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        
class CommentsForm (forms.ModelForm):
    class Meta:
        model= Comment
        fields = ('text',)

