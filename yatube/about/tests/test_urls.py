from django.test import TestCase, Client


class TestUrlAbout (TestCase):
    def setUp(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        '''Проверка доступности адреса'''
        url_names = ('/author/', '/tech/')
        for addres in url_names:
            with self.subTest(addres=addres):
                respons = TestUrlAbout.guest_client.get(addres)
                self.assertEqual(respons.status_code, 200)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        templates_url_name = {'about/author.html': '/author/',
                              'about/author.html': '/tech/'}
        for template, address in templates_url_name.items():
            with self.subTest(address=address):
                response = TestUrlAbout.guest_client.get(address)
                self.assertTemplateUsed(response, template)
