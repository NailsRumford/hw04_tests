from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify


User = get_user_model()


class Group(models.Model):
    """Модель группы сообщества"""
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Введите название группы'
                             )
    slug = models.SlugField(unique=True,
                            null=True,
                            verbose_name='Адресс для страницы группы',
                            help_text=('Введенный вами текст будет'
                                       ' автоматически переведен в'
                                       ' транслит и обрезан до 100 символов.')
                            )
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Введите описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        else:
            self.slug = slugify(self.slug)[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    """Модель поста"""
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет отнаситься пост'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.text[:15]}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    