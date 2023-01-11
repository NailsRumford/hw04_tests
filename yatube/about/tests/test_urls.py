from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse

class TestUrlAbout (TestCase):
    def test_url_exists_at_desired_location(self):
        '''Проверка доступности адреса'''
        path_list = (reverse('about:author'), reverse('about:tech'))
        for path in path_list:
            with self.subTest(addres = path):
                respons = Client.get(path)
                self.assertEqual(respons.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        templates_url_name = {'/author/': 'about/author.html',
                              '/tech/': 'about/tech.html'}
        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = Client(address)
                self.assertTemplateUsed(response, template)
