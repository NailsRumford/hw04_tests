from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class TestUrlAbout (TestCase):
    def test_url_exists_at_desired_location(self):
        '''Проверка доступности адреса'''
        path_list = (reverse('about:author'), reverse('about:tech'))
        for path in path_list:
            with self.subTest(addres=path):
                respons = Client.get(path)
                self.assertEqual(respons.status_code, HTTPStatus.OK)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        path_template_name = {'/author/': 'about/author.html',
                              '/tech/': 'about/tech.html'}
        for path, template in path_template_name.items():
            with self.subTest(address=path):
                response = Client(path)
                self.assertTemplateUsed(response, template)
