from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus
from mixer.backend.django import mixer
from django.core.paginator import Page
from posts.forms import PostForm
from posts.models import Group, Post
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class FixtureForTest (TestCase):

    def setUp(self):
        self.user = mixer.blend(User)
        self.goust_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def assertFirstPostMeetsExpectations(self, response, expected_value):
        object_list = self.get_field_from_context(response.context, Page)
        self.assertEqual(object_list[0], expected_value)

    def assertPaginatorWorkDone(self, user, path, all_post_count):
        """
        Пагинатор выдает ожидаемое количество постов на странице
        """
        response_first_page = user.get(path)
        response_second_page = user.get(path + '?page=2')
        expected_posts_to_the_second_page = None
        if all_post_count % POSTS_PER_PAGE != 0:
            expected_posts_to_the_second_page = all_post_count % POSTS_PER_PAGE
        else:
            expected_posts_to_the_second_page = POSTS_PER_PAGE

        self.assertEqual(len(self.get_field_from_context(response_first_page.context, Page)),
                         POSTS_PER_PAGE)
        self.assertEqual(len(self.get_field_from_context(response_second_page.context, Page)),
                         expected_posts_to_the_second_page)

    def get_field_from_context(self, context, field_type):
        for field in context.keys():
            if field not in ('user', 'request') and isinstance(context[field], field_type):
                return context[field]
        return


class IndexViewTest(FixtureForTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/index.html'
        cls.path = reverse('posts:index')
        mixer.cycle(POSTS_PER_PAGE).blend(Post)

    def test_index_context_views(self):
        expected_post = mixer.blend(Post)
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFirstPostMeetsExpectations(response, expected_post)

    def test_index_pagination(self):
        self.assertPaginatorWorkDone(
            self.goust_user, self.path, Post.objects.all().count())

    def test_index_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)


class GroupPostsViewTest (FixtureForTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/group_list.html'
        cls.group = mixer.blend(Group)
        cls.path = reverse('posts:group_list', args=(cls.group.slug,))
        mixer.cycle(POSTS_PER_PAGE).blend(Post, group=cls.group)
        
    def setUp(self):
        self.user = mixer.blend(User)
        self.goust_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_group_posts_context(self):
        expected_post = mixer.blend(Post, group=self.group)
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFirstPostMeetsExpectations(response, expected_post)
        self.assertEqual(self.get_field_from_context(response.context, Group), self.group)

    def test_group_posts_pagination(self):
        self.assertPaginatorWorkDone(
            self.goust_user, self.path, self.group.posts.all().count())

    def test_group_posts_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)
        
class ProfileViewTest (FixtureForTest):       
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/profile.html'
        cls.author = mixer.blend(User)
        cls.author_user = Client()
        cls.author_user.force_login(cls.author)
        cls.path = reverse('posts:profile', args=(cls.author.username,))
        mixer.cycle(POSTS_PER_PAGE).blend(Post, author=cls.author)
    
    def test_profile_context_views(self):
        expected_post = Post.objects.filter(author=self.author).first()
        response = self.author_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFirstPostMeetsExpectations(response, expected_post)
    
    def test_profile_pagination(self):
        self.assertPaginatorWorkDone(
            self.author_user, self.path, Post.objects.filter(author=self.user).count())
    
    def test_profile_template(self):
        response = self.author_user.get(self.path)
        self.assertTemplateUsed(response, self.template)


# class PostsViewsTest(TestCase):
#
#    @classmethod
#    def setUpClass(cls):
#        super().setUpClass()
#        cls.user = User.objects.create_user(username='TestUser')
#        cls.goust_user = Client()
#        cls.authorized_user = Client()
#        cls.authorized_user.force_login(cls.user)
#        cls.group_one = Group.objects.create(
#            title="Тестовая группа 1 ",
#            slug="Тестовый_слаг",
#            description="Тестовое описание1"
#        )
#        cls.group_two = Group.objects.create(
#            title="Тестовая группа 2 ",
#            slug="Тестовый_слаг2",
#            description="Тестовое описание2"
#        )
#        cls.posts = mixer.cycle(13).blend(
#            Post, author=PostsViewsTest.user, group=PostsViewsTest.group_one)
#
#    def setUp(self):
#
#
#    def test_pages_uses_correct_template(self):
#        """URL-адрес использует соответствующий шаблон."""
#        templates_pages_names = {
#            reverse('posts:index'): 'posts/index.html',
#            reverse('posts:group_list',
#                    kwargs={'slug': PostsViewsTest.group_one.slug}):
#            'posts/group_list.html',
#            reverse('posts:profile',
#                    kwargs={'username': str(PostsViewsTest.user)}):
#            'posts/profile.html',
#            reverse('posts:post_detail', kwargs={'post_id': 1}):
#                'posts/post_detail.html',
#            reverse('posts:post_edit', kwargs={'post_id': 1}):
#            'posts/create_post.html',
#            reverse('posts:post_create'): 'posts/create_post.html'
#        }
#
#        for path, template in templates_pages_names.items():
#            with self.subTest(Address=path):
#                response = PostsViewsTest.authorized_user.get(path)
#                self.assertTemplateUsed(response, template)
#
#    def test_index_page_show_correct_context(self):
#        """На странице Page показан соответсвующий контент"""
#        data_for_test = {reverse('posts:index'):
#                         (mixer.blend(Post,
#                                      author=PostsViewsTest.author,
#                                      group=PostsViewsTest.group_two),
#                          Page),
#                         }
#        for path, (expected_value, feild_type) in data_for_test.items():
#            response = PostsViewsTest.author_user.get(path)
#            test_object = self.get_object_response_context(
#                response, feild_type)
#            if isinstance(test_object, Page):
#                test_object = test_object.object_list[0]
#            self.chek_context(test_object, expected_value)
#
#
#
#    def test_group_list_page_show_correct_context(self):
#        """На странице group list показан соответсвующий контент"""
#        expected_value = mixer.blend(
#            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
#        path = reverse('posts:group_list', kwargs={
#                       'slug': expected_value.group.slug})
#        response = PostsViewsTest.authorized_user.get(path)
#        paginator_page = self.get_object_response_context(response, Page)
#        context_object = paginator_page.object_list[0]
#        self.chek_context(context_object,expected_value)
#
#    def test_profile_page_show_correct_context(self):
#        """На странице profile показан соответсвующий контент"""
#        expected_value = mixer.blend(
#            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
#        path = reverse('posts:profile', kwargs={
#                       'username': str(PostsViewsTest.author)})
#        response = PostsViewsTest.author_user.get(path)
#        paginator_page = self.get_object_response_context(response, Page)
#        context_object = paginator_page.object_list[0]
#        self.chek_context(context_object, expected_value)
#
#    def test_post_detail_page_show_correct_context(self):
#        """На странице post detail показан соответсвующий контент"""
#        expected_value = mixer.blend(
#            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
#        path = reverse('posts:post_detail', kwargs={
#                       'post_id': expected_value.id})
#        response = self.authorized_user.get(path)
#        context_object = self.get_object_response_context(response, Post)
#        self.chek_context(context_object, expected_value)
#
#    def test_post_create_show_correct_context(self):
#        """На странице post create показан соответсвующий контент"""
#        expected_value = PostForm()
#        path = reverse('posts:post_create')
#        response = self.authorized_user.get(path)
#        test_value = self.get_object_response_context(
#            response, PostForm)
#        for field, value in expected_value.fields.items():
#            with self.subTest(field=field):
#                self.assertIsInstance(test_value.fields[field], type(value))
#
#    def test_post_edit_page_show_correct_context(self):
#        """На странице post edit показан соответсвующий контент"""
#        instance = mixer.blend(
#            Post, author=PostsViewsTest.author, group=PostsViewsTest.group_two)
#        expected_value = PostForm(instance=instance)
#        path = reverse('posts:post_edit', kwargs={'post_id': instance.id})
#        response = PostsViewsTest.author_user.get(path)
#        test_value = PostsViewsTest.get_object_response_context(
#            response, PostForm)
#        with self.subTest():
#            self.assertEqual(test_value.initial, expected_value.initial)
#
#    def test_first_page_contains_ten_records(self):
#        """ Проверяет наличие Paginatora и количество постов на странице"""
#        data_for_test = (reverse('posts:index'),
#                         reverse('posts:group_list', kwargs={
#                                 'slug': PostsViewsTest.group_one.slug}),
#                         reverse('posts:profile', kwargs={
#                                 'username': str(PostsViewsTest.user)}))
#        for path in data_for_test:
#            response = PostsViewsTest.authorized_user.get(path)
#            paginator_page = self.get_object_response_context(response, Page)
#            with self.subTest(address=path):
#                self.assertIsInstance(paginator_page, Page)
#                self.assertEqual(paginator_page.paginator.per_page, 10)
#
