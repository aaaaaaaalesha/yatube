from django.test import TestCase, Client
from http import HTTPStatus


class AboutUrlTest(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        url_name_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for url_name, template in url_name_templates.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
