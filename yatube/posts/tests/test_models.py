from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


class PostModelTest(TestCase):
    user: User
    post: Post
    group: Group
    comment: Comment
    follow: Follow

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='authenticated',
        )
        cls.post = Post.objects.create(
            author=PostModelTest.user,
            text='Это тестовый пост. Не дай Бог попасть ему в прод!',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Это тестовая группа. Не дай Бог попасть ей в прод!',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cls.author = User.objects.create_user(
            username='author',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        """Testing models' __str__ method."""
        post = PostModelTest.post
        group = PostModelTest.group
        model_objnames = {
            PostModelTest.post: post.text[:15],
            PostModelTest.group: group.title,
        }
        for model, string_name in model_objnames.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), string_name)

    def test_verbose_names(self):
        """Testing fields' verbose names of models."""
        list_cases = [
            (PostModelTest.post, {
                'text': 'Текст поста',
                'pub_date': 'Дата создания',
                'author': 'Автор',
                'group': 'Группа',
            }),
            (PostModelTest.group, {
                'title': 'Название группы',
                'slug': 'Слаг группы',
                'description': 'Описание',
            }),
            (PostModelTest.comment, {
                'post': 'Комментарий',
                'author': 'Автор',
                'text': 'Текст комментария',
            }),
            (PostModelTest.follow, {
                'user': 'Подписчик',
                'author': 'Автор',
            }),
        ]

        for model, field_verboses in list_cases:
            for field, expected_verbose in field_verboses.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_verbose,
                    )

    def test_help_text(self):
        """Testing fields' help texts of models."""
        list_cases = [
            (PostModelTest.post, {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
            }),
            (PostModelTest.group, {
                'title': 'Введите название группы',
                'description': 'Укажите описание группы',
            }),
            (PostModelTest.comment, {
                'text': 'Напишите комментарий',
            }),
        ]

        for model, field_help_text in list_cases:
            for field, expected_help_text in field_help_text.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        expected_help_text,
                    )
