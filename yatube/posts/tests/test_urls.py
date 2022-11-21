from django.test import TestCase, Client
from http import HTTPStatus
from enum import Enum

from ..models import User, Group, Post
from .utlis import URLS, TEMPLATES


class PostsURLTest(TestCase):
    GROUP_SLUG = 'test_group'
    POST_ID: int

    user: User
    another_user: User
    post: Post
    group: Group

    class AccessRight(Enum):
        """Access rights for posts pages."""
        ALL, AUTHORIZED, AUTHOR = range(3)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа любителей тестов',
            slug=cls.GROUP_SLUG,
            description='Это тестовая группа',
        )

        cls.user = User.objects.create_user(username='nonamed')
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.user,
            group=cls.group,
        )
        cls.another_user = User.objects.create_user(username='dog')

    def setUp(self):
        # Unauthorized client.
        self.guest_client = Client()
        # Authorized authored client.
        self.authorized_authored_client = Client()
        self.authorized_authored_client.force_login(
            PostsURLTest.user
        )
        # Authorized unauthored client.
        self.authorized_client = Client()
        self.authorized_client.force_login(self.another_user)

    def test_unexisting_page(self):
        unexisting_url_name = '/unexisting_page/'
        for client in (self.guest_client, self.authorized_client):
            response = client.get(unexisting_url_name)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """
        Testing URL name uses the appropriate template.
        """
        slug = PostsURLTest.GROUP_SLUG
        user = PostsURLTest.user
        post = PostsURLTest.post
        access_right_cases = {
            self.AccessRight.ALL: {
                URLS['index']():
                    TEMPLATES['index'],
                URLS['group_list']({'slug': slug}):
                    TEMPLATES['group_list'],
                URLS['profile']({'username': user.username}):
                    TEMPLATES['profile'],
                URLS['post_detail']({'post_id': post.pk}):
                    TEMPLATES['post_detail'],
            },
            self.AccessRight.AUTHOR: {
                URLS['post_edit']({'post_id': post.pk}):
                    TEMPLATES['post_create'],
            },
            self.AccessRight.AUTHORIZED: {
                URLS['post_create']():
                    TEMPLATES['post_create'],
                URLS['follow_index']():
                    TEMPLATES['follow_index']
            }

        }

        for access_right, url_name_templates in access_right_cases.items():
            for url_name, template in url_name_templates.items():
                with self.subTest(url_name=url_name, template=template):
                    response = self.authorized_authored_client.get(url_name)
                    self.assertTemplateUsed(response, template)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

            if access_right == self.AccessRight.AUTHORIZED:
                for url_name, template in url_name_templates.items():
                    with self.subTest(url_name=url_name, authorized=True):
                        response = self.guest_client.get(url_name, follow=True)
                        self.assertRedirects(
                            response,
                            f'/auth/login/?next={url_name}'
                        )
                continue

            if access_right == self.AccessRight.AUTHOR:
                for url_name, template in url_name_templates.items():
                    with self.subTest(url_name=url_name, authorized=False):
                        response = self.guest_client.get(url_name, follow=True)
                        self.assertRedirects(response,
                                             f'/auth/login/?next={url_name}')

                    with self.subTest(url_name=url_name, authored=False):
                        response = self.authorized_client.get(url_name,
                                                              follow=True)
                        self.assertRedirects(response, f'/posts/{post.pk}/')
