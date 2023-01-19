from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from mixer.backend.django import mixer
from http import HTTPStatus
from posts.models import Post, Group


User = get_user_model()


class URLsTest(TestCase):

    def setUp(self):
        self.user = mixer.blend(User)
        self.group = mixer.blend(Group)
        self.post = mixer.blend(Post, author=self.user, group=self.group)
        self.goust_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_public_urls(self):
        """
        Публичные urls
        (главная, профиль, группа, одиночный пост)
        работают для неавторизованного пользователя
        """
        path_list = (reverse('posts:index'),
                     reverse('posts:group_list', args=(self.group.slug,)),
                     reverse('posts:profile', args=(self.user.username,)),
                     reverse('posts:post_detail', args=(self.post.id,))
                     )

        for path in path_list:
            with self.subTest(path=path):
                response = self.goust_user.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls(self):
        """
        Приватные urls
        (создание-редактирование)
        работают для автаризованного пользователя
        """
        path_list = (reverse('posts:post_create'),
                     reverse('posts:post_edit', args=(self.post.id,)))

        for path in path_list:
            with self.subTest(url=path):
                response = self.authorized_user.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_access(self):
        """
        Гость не может получить доступк приватным урлам,
        """
        path_list = (
            (reverse('posts:post_create'),
             '/auth/login/?next=' + reverse('posts:post_create')),
            (reverse('posts:post_edit', args=(self.post.id,)),
             '/auth/login/?next=' + reverse('posts:post_edit',
                                            args=(self.post.id,)))
        )

        for path, expected_redirect_path in path_list:
            with self.subTest(address=path):
                response = self.goust_user.get(path)
                self.assertRedirects(response, expected_redirect_path)

    def test_non_author_edit(self):
        """
        Не автор поста не может редактировать его
        """
        non_author_user = Client()
        non_author_user.force_login(user=mixer.blend(User))
        path = reverse('posts:post_edit', args=(self.post.id,))
        response = non_author_user.get(path)
        expected_redirect_path = reverse(
            'posts:post_detail', args=(self.post.id,))
        self.assertRedirects(response, expected_redirect_path)

    def test_templates(self):
        """
        Используются коректные шаблоны
        """
        expected_template = [
            (reverse('posts:index'),
             'posts/index.html'),
            (reverse('posts:group_list',
                     args=(self.group.slug,)),
             'posts/group_list.html'),
            (reverse('posts:profile',
                     args=(self.user.username,)),
             'posts/profile.html'),
            (reverse('posts:post_detail',
                     args=(self.post.id,)),
             'posts/post_detail.html'),
            (reverse('posts:post_create'),
             'posts/create_post.html'),
            (reverse('posts:post_edit',
                     args=(self.post.id,)),
             'posts/create_post.html'),
        ]
        for path, template in expected_template:
            with self.subTest(address=path):
                response = self.authorized_user.get(path)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """
        Несуществующая страница вернет ошибку 404
        """
        data_for_test = ('/group/unexisting_page/',
                         '/profile/unexisting_page/')
        for address in data_for_test:
            with self.subTest(test_address=address):
                response_goust_user = self.goust_user.get(address)
                response_authorized_user = self.authorized_user.get(address)
                self.assertEqual(response_goust_user.status_code,
                                 HTTPStatus.NOT_FOUND)
                self.assertEqual(response_authorized_user.status_code,
                                 HTTPStatus.NOT_FOUND)
