from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UsersURLTest(TestCase):
    user: User

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='noname',
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTest.user)

    def test_urls_uses_correct_template(self):
        url_templates = {
            '/auth/signup/':
                'users/signup.html',
            '/auth/logout/':
                'users/logged_out.html',
            '/auth/login/':
                'users/login.html',
            '/auth/password_change/':
                'users/password/password_change_form.html',
            '/auth/password_change/done/':
                'users/password/password_change_done.html',
            '/auth/password_reset/':
                'users/password/password_reset_form.html',
            '/auth/password_reset/done/':
                'users/password/password_reset_done.html',
            '/auth/reset/done/':
                'users/password/password_reset_complete.html',
        }

        for url, template in url_templates.items():
            if url.startswith('/auth/password_change/'):
                with self.subTest(url=url, authorized=False):
                    response = self.guest_client.get(url)
                    redirected_url = f'/auth/login/?next={url}'
                    self.assertRedirects(response, redirected_url)
                    continue

            with self.subTest(url=url, authorized=True):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
