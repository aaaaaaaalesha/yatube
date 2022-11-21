from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.shortcuts import get_object_or_404
from django import forms

from http import HTTPStatus

from ..models import User, Post, Group, Follow, POSTS_PER_PAGE
from .utlis import URLS, TEMPLATES


class PostsViewTest(TestCase):
    POSTS_COUNT = 15

    user: User
    group: Group
    another_group: Group
    image: SimpleUploadedFile

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа любителей тестов',
            slug='test_group',
            description='Это тестовая группа',
        )
        cls.another_group = Group.objects.create(
            title='Группа ненавистников тестов',
            slug='test_haters',
            description='Это тестовая группа',
        )
        cls.user = User.objects.create_user(username='nonamed')

        Post.objects.bulk_create((
            Post(
                text=f'Текст {i} тестового поста ',
                author=cls.user,
                group=PostsViewTest.group,
            )
            for i in range(cls.POSTS_COUNT)
        ))

        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewTest.user)
        self.guest_client = Client()

    def test_views_uses_correct_template(self):
        post = get_object_or_404(Post, pk=3)
        page_name_templates = {
            URLS['index']():
                TEMPLATES['index'],
            URLS['group_list']({'slug': 'test_group'}):
                TEMPLATES['group_list'],
            URLS['profile']({'username': 'nonamed'}):
                TEMPLATES['profile'],
            URLS['post_detail']({'post_id': post.id}):
                TEMPLATES['post_detail'],
            URLS['post_create']():
                TEMPLATES['post_create'],
            URLS['post_edit']({'post_id': post.id}):
                TEMPLATES['post_edit'],
            URLS['follow_index']():
                TEMPLATES['follow_index'],
        }

        for reverse_name, template in page_name_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_page_shows_correct_context(self):
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(
                    URLS['post_create']()
                )
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_paginator(self):
        urls = (
            URLS['index'](),
            URLS['group_list']({'slug': 'test_group'}),
            URLS['profile']({'username': 'nonamed'}),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    max(0, POSTS_PER_PAGE)
                )
                response = self.authorized_client.get(f'{url}?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    max(0, PostsViewTest.POSTS_COUNT - POSTS_PER_PAGE)
                )

        url = URLS['group_list']({'slug': 'test_haters'})
        with self.subTest(url=url):
            response = self.client.get(url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                max(0, PostsViewTest.POSTS_COUNT - 2 * POSTS_PER_PAGE)
            )

    def test_post_scope(self):
        post = Post.objects.create(
            text='Когда-нибудь тесты будут писать нейросети...',
            author=PostsViewTest.user,
            group=PostsViewTest.another_group,
        )

        response = self.authorized_client.get(
            URLS['post_detail']({'post_id': post.id}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        in_scope_urls = [
            URLS['index'](),
            URLS['group_list']({'slug': post.group.slug}),
            URLS['profile']({'username': post.author}),
        ]
        for url in in_scope_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                page_obj = response.context['page_obj']
                self.assertIn(post, page_obj.object_list)

        another_user = User.objects.create_user(username='another_nonamed')
        out_scope_urls = [
            URLS['group_list']({'slug': PostsViewTest.group.slug}),
            URLS['profile']({'username': another_user.username}),
        ]
        for url in out_scope_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                page_obj = response.context['page_obj']
                self.assertNotIn(post, page_obj.object_list)

    def test_posts_image_in_context(self):

        imaged_post = Post.objects.create(
            text='Это текст с картинкой',
            author=PostsViewTest.user,
            group=PostsViewTest.group,
            image=PostsViewTest.image,
        )

        urls = (
            URLS['index'](),
            URLS['profile']({'username': PostsViewTest.user.username}),
            URLS['group_list']({'slug': PostsViewTest.group.slug}),
            URLS['post_detail']({'post_id': imaged_post.id})
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if url == URLS['post_detail']({'post_id': imaged_post.id}):
                    post = response.context['post']
                else:
                    post = response.context['page_obj'][0]

                self.assertEqual(post.image, imaged_post.image)

    def test_cache_index(self):
        post = Post.objects.create(
            text='Кешируй меня полностью',
            author=PostsViewTest.user,
            group=PostsViewTest.group,
        )
        response = self.guest_client.get(URLS['index']())
        content = response.content
        post.delete()
        response_again = self.guest_client.get(URLS['index']())
        content_again = response_again.content

        # При повторном запросе получаем закешированную страницу с
        # удалённым постом: контент совпадает.
        self.assertEqual(content, content_again)
        cache.clear()
        response_again = self.guest_client.get(URLS['index']())
        content_again = response_again.content
        # При очистке кеша получим отличную страницу: контент не совпадает.
        self.assertNotEqual(content, content_again)

    def test_follow_unfollow(self):
        response = self.guest_client.get(URLS['follow_index']())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        follower = User.objects.create_user(username='follower')
        author = PostsViewTest.user
        follower_client = Client()
        # Follow the author.
        follower_client.force_login(user=follower)
        response = follower_client.post(
            URLS['profile_follow']({'username': author.username})
        )
        self.assertRedirects(
            response,
            URLS['profile']({'username': author.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=follower, author=author
            ).exists()
        )
        # Check that follow_index page shows correct posts.
        response = follower_client.get(URLS['follow_index']())
        self.assertEqual(
            response.context.get('page_obj').object_list,
            list(Post.objects.filter(author=author)[:POSTS_PER_PAGE])
        )
        #  Posts page is empty for those who do not subscribe to it.
        response = self.authorized_client.get(URLS['follow_index']())
        self.assertFalse(
            Follow.objects.filter(
                user=author, author=author
            ).exists()
        )
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            0
        )

        # Unfollow.
        response = follower_client.post(
            URLS['profile_unfollow']({'username': author.username})
        )
        self.assertRedirects(
            response,
            URLS['profile']({'username': author.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=follower, author=author
            ).exists()
        )
