from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from http import HTTPStatus

User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author_user = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.user = User.objects.create_user(username='testUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='Тестовый пост',
            group=cls.group
        )

    def test_URL_for_all_users(self):
        """
        Проверка URL доступных для всех пользовотелей.
        data_for_test = {address:address_template}
        """
        data_for_test = {'/': 'posts/index.html',
                         f'/group/{PostsURLTest.group.slug}/':
                             'posts/group_list.html',
                         f'/profile/{PostsURLTest.user}/':
                             'posts/profile.html'}

        for address, template in data_for_test.items():
            with self.subTest(test_address=address):
                response = PostsURLTest.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_URL_for_authorized_user(self):
        """
        Проверка URL для авторизованного пользователя
        data_for_test = {address:(adress_template, redirect_address)}
        """
        data_for_test = {
            '/create/': ('posts/create_post.html',
                         '/auth/login/?next=/create/')}

        for address, (template, redirect_address) in data_for_test.items():
            with self.subTest(test_address=address):
                response_authorized_users = PostsURLTest.authorized_client.get(
                    address)
                response_guest_users = PostsURLTest.guest_client.get(
                    address, follow=True)
                self.assertEqual(
                    response_authorized_users.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_authorized_users, template)
                self.assertRedirects(response_guest_users, redirect_address)

    def test_URL_for_autor_user(self):
        """
        Провверка URL для автора
        data_for_test = {address:(adress_template, redirect_address)}
        """
        data_for_test = {f'/posts/{PostsURLTest.post.id}/edit/': (
            'posts/create_post.html', f'/posts/{PostsURLTest.post.id}/')}
        for address, (template, redirect_address) in data_for_test.items():
            with self.subTest(test_address=address):
                response_author_user = PostsURLTest.author_client.get(address)
                response_authorized_user = PostsURLTest.authorized_client.get(
                    address)
                response_guest_users = PostsURLTest.guest_client.get(address)
                self.assertEqual(
                    response_author_user.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response_author_user, template)
                self.assertRedirects(
                    response_authorized_user, redirect_address)
                self.assertRedirects(response_guest_users,
                                     ('/auth/login/?next=' + address))

    def test_unexisting_page(self):
        data_for_test = {'/group/unexisting_page/',
                         '/profile/unexisting_page/'}
        for address in data_for_test:
            with self.subTest(test_address=address):
                response_goust_user = PostsURLTest.guest_client.get(address)
                response_authorized_user = PostsURLTest.author_client.get(
                    address)
                self.assertEqual(
                    response_goust_user.status_code, HTTPStatus.NOT_FOUND)
                self.assertEqual(
                    response_authorized_user.status_code, HTTPStatus.NOT_FOUND)
