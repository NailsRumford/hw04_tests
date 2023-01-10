from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from django.core.paginator import Page
from posts.forms import PostForm
from mixer.backend.django import mixer
from django.core.paginator import Page
User = get_user_model()


class PostsViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.goust_user = Client()
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.author_user = Client()
        cls.author_user.force_login(cls.author)
        cls.group_one = Group.objects.create(
            title="Тестовая группа 1 ",
            slug="Тестовый_слаг",
            description="Тестовое описание1"
        )
        cls.group_two = Group.objects.create(
            title="Тестовая группа 2 ",
            slug="Тестовый_слаг2",
            description="Тестовое описание2"
        )
        cls.posts = mixer.cycle(13).blend(
            Post, author=PostsViewsTest.user, group=PostsViewsTest.group_one)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTest.group_one.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': str(PostsViewsTest.user)}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        for path, template in templates_pages_names.items():
            with self.subTest(Address=path):
                response = PostsViewsTest.authorized_user.get(path)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """На странице Page показан соответсвующий контент"""
        data_for_test = {reverse('posts:index'):
                         (mixer.blend(Post,
                                      author=PostsViewsTest.author,
                                      group=PostsViewsTest.group_two),
                          Page),
                         }
        for path, (expected_value, feild_type) in data_for_test.items():
            response = PostsViewsTest.author_user.get(path)
            test_object = self.get_object_response_context(
                response, feild_type)
            if isinstance(test_object, Page):
                test_object = test_object.object_list[0]
            with self.subTest():
                self.assertEqual(test_object.text, expected_value.text)
                self.assertEqual(test_object.author, expected_value.author)
                self.assertEqual(test_object.group, expected_value.group)

    def test_group_list_page_show_correct_context(self):
        """На странице group list показан соответсвующий контент"""
        expected_value = mixer.blend(
            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
        path = reverse('posts:group_list', kwargs={
                       'slug': expected_value.group.slug})
        response = PostsViewsTest.authorized_user.get(path)
        paginator_page = self.get_object_response_context(response, Page)
        test_post = paginator_page.object_list[0]
        self.assertEqual(test_post.text, expected_value.text)
        self.assertEqual(test_post.author, expected_value.author)
        self.assertEqual(test_post.group, expected_value.group)

    def test_profile_page_show_correct_context(self):
        """На странице profile показан соответсвующий контент"""
        expected_value = mixer.blend(
            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
        path = reverse('posts:profile', kwargs={
                       'username': str(PostsViewsTest.author)})
        response = PostsViewsTest.author_user.get(path)
        paginator_page = self.get_object_response_context(response, Page)
        test_post = paginator_page.object_list[0]
        self.assertEqual(test_post.text, expected_value.text)
        self.assertEqual(test_post.author, expected_value.author)
        self.assertEqual(test_post.group, expected_value.group)

    def test_post_detail_page_show_correct_context(self):
        """На странице post detail показан соответсвующий контент"""
        expected_value = mixer.blend(
            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
        path = reverse('posts:post_detail', kwargs={
                       'post_id': expected_value.id})
        response = PostsViewsTest.authorized_user.get(path)
        test_value = PostsViewsTest.get_object_response_context(response, Post)
        self.assertEqual(test_value.text, expected_value.text)
        self.assertEqual(test_value.author, expected_value.author)
        self.assertEqual(test_value.group, expected_value.group)

    def test_post_create_show_correct_context(self):
        """На странице post create показан соответсвующий контент"""
        expected_value = PostForm()
        path = reverse('posts:post_create')
        response = PostsViewsTest.authorized_user.get(path)
        test_value = PostsViewsTest.get_object_response_context(
            response, PostForm)
        for field, value in expected_value.fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(test_value.fields[field], type(value))

    def test_post_edit_page_show_correct_context(self):
        """На странице post edit показан соответсвующий контент"""
        instance = mixer.blend(
            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
        expected_value = PostForm(instance=instance)
        path = reverse('posts:post_edit', kwargs={'post_id': instance.id})
        response = PostsViewsTest.author_user.get(path)
        test_value = PostsViewsTest.get_object_response_context(
            response, PostForm)
        with self.subTest():
            self.assertEqual(test_value.initial, expected_value.initial)

    def test_first_page_contains_ten_records(self):
        """ Проверяет наличие Paginatora и количество постов на странице"""
        data_for_test = (reverse('posts:index'),
                         reverse('posts:group_list', kwargs={
                                 'slug': PostsViewsTest.group_one.slug}),
                         reverse('posts:profile', kwargs={
                                 'username': str(PostsViewsTest.user)}))
        for path in data_for_test:
            response = PostsViewsTest.authorized_user.get(path)
            paginator_page = self.get_object_response_context(response, Page)
            with self.subTest(address=path):
                self.assertIsInstance(paginator_page, Page)
                self.assertEqual(paginator_page.paginator.per_page, 10)

    @classmethod
    def get_object_response_context(cls, response, field_type):
        context = response.context
        for field in context.keys():
            if isinstance(context[field], field_type):
                return context[field]
