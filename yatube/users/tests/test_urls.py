from django.test import TestCase, Client()
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UsersURLTest (TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.goust_user = Client()

    def test_URL_for_all_users(self):
        """
        Проверка URL доступных для всех пользовотелей.
        data_for_test = {address:address_template}
        """
        data_for_test = {'/login/', '/logout/', '/singup/',
                         '/password_reset/', '/password_reset/done/', }
