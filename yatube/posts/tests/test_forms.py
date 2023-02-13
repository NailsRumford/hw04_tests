from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from mixer.backend.django import mixer
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.tests.setting import BaseTestCase
from posts.models import Group, Post, Comment


User = get_user_model()

class PostFormTest (BaseTestCase):

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
    def tearDown(self) -> None:
        super().tearDown()
        Post.objects.all().delete()

    def test_valid_form_creates_post(self):
        """
        Форма создает пост с ожидаемыми значениями
        """
        post_count = Post.objects.count()
        path = reverse('posts:post_create')
        expected_redirect_path = reverse(
            'posts:profile', args=(self.user.username,))
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        
        form_data = {
            'text': 'test_text',
            'group': self.group.id,
            'image': uploaded
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


class CommentsFormTest (BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.goust_user = Client()
        cls.post = mixer.blend(Post)
        cls.path = reverse('posts:add_comment', args=(cls.post.id,))
        
    def test_authorized_user_can_comment_post(self):
        comments_count = Comment.objects.count()
        form_data= {'text': 'test text'}
        response = self.authorized_user.post(self.path, data=form_data)
        self.assertEqual(Comment.objects.count(),comments_count+1,
                         'Автаризованный пользователь не может коментировать пост')
        
    def test_goust_user_can_comment_post(self):
        comments_count = Comment.objects.count()
        form_data= {'text': 'test text'}
        response = self.goust_user.post(self.path, data=form_data)
        self.assertNotEqual(Comment.objects.count(),comments_count+1,
                         'Неавтаризованный пользователь может коментировать пост')
        