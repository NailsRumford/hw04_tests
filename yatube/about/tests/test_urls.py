from django.test import TestCase, Client
from http import HTTPStatus


class TestUrlAbout (TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        '''Проверка доступности адреса'''
        url_names = ('/author/', '/tech/')
        for addres in url_names:
            with self.subTest(addres=addres):
                respons = self.guest_client.get(addres)
                self.assertEqual(respons.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        templates_url_name = {'/author/': 'about/author.html',
                              '/tech/': 'about/tech.html'}
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
