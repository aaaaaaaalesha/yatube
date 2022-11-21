import shutil
import tempfile

from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from ..models import Post, User, Comment
from .utlis import URLS

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    user: User
    another_user: User
    post: Post
    another_post: Post

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='nonamed')
        cls.another_user = User.objects.create_user(username='named')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.another_post = Post.objects.create(
            text='Другой тестовый текст',
            author=cls.user,
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

        self.guest_client = Client()
        self.guest_client.force_login(PostCreateFormTests.another_user)

        self.guest_client = Client()

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Заполняем форму создания поста',
            'image': SimpleUploadedFile(
                name='small.gif',
                content=PostCreateFormTests.small_gif,
                content_type='image/gif'
            ),
        }
        response = self.authorized_client.post(
            URLS['post_create'](),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            URLS['profile']({'username': 'nonamed'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Заполняем форму создания поста').exists()
        )

    def test_post_edit(self):
        post = PostCreateFormTests.another_post
        response = self.authorized_client.post(
            URLS['post_edit']({'post_id': post.id}),
            data={
                'text': 'Изменяем текст поста',
                'image': SimpleUploadedFile(
                    name='small.gif',
                    content=PostCreateFormTests.small_gif,
                    content_type='image/gif'
                ),
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            URLS['post_detail']({'post_id': post.id})
        )
        self.assertTrue(
            Post.objects.filter(text='Изменяем текст поста').exists()
        )

    def test_not_create_post(self):
        # Guest.
        posts_count = Post.objects.count()
        self.guest_client.post(
            URLS['post_create'](),
            data={'text': 'Заполняем форму создания поста'},
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_not_edit(self):
        post = PostCreateFormTests.post
        # Guest and not author.
        for client in (self.guest_client, self.guest_client):
            with self.subTest(client=client):
                client.post(
                    URLS['post_edit']({'post_id': post.id}),
                    data={'text': 'Не изменяем текст поста'},
                    follow=True,
                )

                self.assertFalse(
                    Post.objects.filter(
                        text='Не изменяем текст поста'
                    ).exists()
                )


class CommentFormTests(TestCase):
    authored_user: User
    leo_user: User
    post: Post

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authored_user = User.objects.create_user(username='named')
        cls.leo_user = User.objects.create_user(username='leo')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.authored_user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authored_client = Client()
        self.leo_client = Client()

        self.authored_client.force_login(user=CommentFormTests.authored_user)
        self.leo_client.force_login(user=CommentFormTests.leo_user)

    def test_leave_comment(self):
        post = CommentFormTests.post

        for client in (self.leo_client, self.guest_client):
            with self.subTest(client=client):
                comments_count = Comment.objects.count()
                response = self.leo_client.post(
                    URLS['add_comment']({'post_id': post.id}),
                    data={'text': 'Это тестовый комментарий'},
                    follow=True,
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                if client == self.leo_client:
                    comments_count += 1
                    self.assertEqual(Comment.objects.count(), comments_count)

        self.assertTrue(Comment.objects.filter(post=post).exists())
