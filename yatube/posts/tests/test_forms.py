from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

User = get_user_model()


class PostCreateFormTest (TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post)

    def setUp(self) -> None:

        self.user = User.objects.create_user(username='testUser')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создаст записть Post"""
        path = reverse('posts:post_create')
        expected_redirect_path = reverse('posts:profile', kwargs={
                                         'username': str(self.user)})
        post_count = Post.objects.count()
        form_data = {
            'text': 'test_text',
            'group': self.group.id,
        }
        response = self.authorized_user.post(path, data=form_data, follow=True)
        with self.subTest():
            self.assertEqual(Post.objects.count(), post_count + 1)
            self.assertRedirects(response, expected_redirect_path)
            self.assertTrue(
                Post.objects.filter(
                    text='test_text',
                    group=self.group,
                    author=self.user
                ).exists()
            )


class PostEditFormTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = mixer.blend(Group)

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testUser')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.post = mixer.blend(Post, author=self.user)

    def test_post_edit(self):
        """Валидная форма отредактирует записть Post"""
        path = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        expected_redirect_path = reverse('posts:post_detail', kwargs={
                                         'post_id': self.post.id})
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_user.post(path, data=form_data, follow=True)
        self.assertRedirects(response, expected_redirect_path)
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.group.id, form_data['group'])
