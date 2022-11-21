from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

POSTS_PER_PAGE = 10

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        help_text='Введите название группы',
        max_length=200,
    )
    slug = models.SlugField(
        'Слаг группы',
        unique=True,
    )
    description = models.TextField(
        'Описание',
        help_text='Укажите описание группы',
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Автор',
        related_name='posts',
        null=True,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name='Группа',
        related_name='posts',
        blank=True,
        null=True,
        help_text='Группа, к которой будет относиться пост',

    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self):
        return self.text[:15]

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        related_name='comments',
        help_text='Оставьте комментарий здесь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Напишите комментарий',
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )
