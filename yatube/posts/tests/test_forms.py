from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostFormTest (TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def setUp(self) -> None:

        self.user = mixer.blend(User)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.post = mixer.blend(Post,
                                author=self.user,
                                group=self.group,
                                )

    def test_valid_form_creates_post(self):
        """
        Форма создает пост с ожидаемыми значениями
        """
        post_count = Post.objects.count()
        path = reverse('posts:post_create')
        expected_redirect_path = reverse(
            'posts:profile', args=(self.user.username,))
        form_data = {
            'text': 'test_text',
            'group': self.group.id,
        }
        response = self.authorized_user.post(path, data=form_data, follow=True)
        first_post_per_page = Post.objects.first()
        self.assertEqual(Post.objects.count(),
                         post_count + 1,
                         "Пост не создался")
        self.assertRedirects(response,
                             expected_redirect_path)
        self.assertEqual(first_post_per_page.text,
                         form_data['text'],
                         "Текст поста не соответствует ожидаемому")
        self.assertEqual(first_post_per_page.group.id,
                         form_data['group'],
                         "Группа поста не соответствует ожидаемой")
        self.assertEqual(first_post_per_page.author, self.user,
                         "Автор поста не соответствует ожидаемому")

    def test_valid_form_edit_post(self):
        """
        Валидная форма отредактирует записть Post
        """
        post_count = Post.objects.count()
        path = reverse('posts:post_edit', args=(self.post.id,))
        expected_redirect_path = reverse(
            'posts:post_detail', args=(self.post.id,))
        form_data = {
            'text': 'test_text',
            'group': mixer.blend(Group).id,
        }
        response = self.authorized_user.post(path, data=form_data, follow=True)
        edited_object = Post.objects.get(id=self.post.id)
        self.assertEqual(Post.objects.count(),
                         post_count,
                         "Пост создался, а не отредактировался")
        self.assertRedirects(response,
                             expected_redirect_path)
        self.assertEqual(edited_object.text,
                         form_data['text'],
                         "Текст поста не соответствует ожидаемому")
        self.assertEqual(edited_object.group.id,
                         form_data['group'],
                         "Группа поста не соответствует ожидаемой")
        self.assertEqual(edited_object.author,
                         self.user,
                         "Автор поста не соответствует ожидаемому")

    def test_unauthorize_user_cannot_send_form(self):
        """
        Неавтаризованный пользователь не сможет отправить форму
        """
        unauthorize_user = Client()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        path_list = (
            (reverse('posts:post_create'),
             '/auth/login/?next=' + reverse('posts:post_create')),
            (reverse('posts:post_edit', args=(self.post.id,)),
             '/auth/login/?next=' + reverse('posts:post_edit',
                                            args=(self.post.id,)))
        )
        post_count = Post.objects.count()
        for path, expected_redirect_path in path_list:
            with self.subTest(path):
                response = unauthorize_user.post(
                    path, data=form_data, follow=True)

                self.assertEqual(Post.objects.count(),
                                 post_count,
                                 "При отправки формы неавторизованным "
                                 "пользователем, число постов изменилось")
                self.assertRedirects(response, expected_redirect_path)
