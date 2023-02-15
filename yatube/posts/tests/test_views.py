from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.test import Client
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Group, Post, Follow
from posts.tests.setting import BaseTestCase
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class FixtureForTest (BaseTestCase):
    def setUp(self) -> None:
        self.faker = Faker()
        cache.clear()
        
    def get_first_post_on_page(self, response):
        page = self.get_field_from_context(response.context, Page)
        post = self.get_field_from_context(response.context, Post)
        if isinstance(page, Page):
            return page[0]
        elif isinstance(post, Post):
            return post
        else:
            return None

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

        first_page_context = self.get_field_from_context(
            response_first_page.context,
            Page
        )
        second_page_context = self.get_field_from_context(
            response_second_page.context,
            Page
        )
        self.assertEqual(len(first_page_context), POSTS_PER_PAGE)
        self.assertEqual(len(second_page_context),
                         expected_posts_to_the_second_page)

    def get_field_from_context(self, context, field_type):
        for field in context.keys():
            if field not in ('user', 'request') and isinstance(context[field],
                                                               field_type):
                return context[field]
        return

    def assertImageIsInContext(self, post, user, path):
        excepted_image = post.image
        cache.clear()
        response = user.get(path)
        test_post = self.get_first_post_on_page(response)
        test_image = test_post.image
        self.assertEqual(excepted_image, test_image)


class IndexViewTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/index.html'
        cls.path = reverse('posts:index')
        cls.user = mixer.blend(User)
        cls.goust_user = Client()
        mixer.cycle(POSTS_PER_PAGE).blend(Post)


    def test_status_code(self):
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_first_post_per_page(self):
        expected_post = mixer.blend(Post)
        response = self.goust_user.get(self.path)
        self.assertFirstPostMeetsExpectations(response, expected_post)

    def test_image_is_in_context(self):
        test_post = mixer.blend(Post)
        self.assertImageIsInContext(test_post, self.goust_user, self.path)

    def test_index_page_caching(self):
        response_before_post_delete = self.goust_user.get(self.path)
        self.get_first_post_on_page(response_before_post_delete).delete()
        response_after_post_delete = self.goust_user.get(self.path)
        cache.clear()
        response_after_cache_delete = self.goust_user.get(self.path)
        self.assertEqual(response_after_post_delete.content,
                         response_after_post_delete.content)
        self.assertNotEqual(response_after_post_delete.content,
                            response_after_cache_delete.content)

    def test_index_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)

    def test_pagination(self):
        self.assertPaginatorWorkDone(
            self.goust_user,
            self.path,
            Post.objects.all().count())


class GroupPostsViewTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/group_list.html'
        cls.group = mixer.blend(Group)
        cls.path = reverse('posts:group_list', args=(cls.group.slug,))
        cls.goust_user = Client()
        mixer.cycle(POSTS_PER_PAGE).blend(Post, group=cls.group)

    def test_status_code(self):
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_in_context(self):
        response = self.goust_user.get(self.path)
        group_from_context = self.get_field_from_context(
            response.context, Group)
        self.assertEqual(group_from_context, self.group)

    def test_first_post_per_page(self):
        expected_post = mixer.blend(Post, group=self.group)
        response = self.goust_user.get(self.path)
        self.assertFirstPostMeetsExpectations(response, expected_post)

    def test_image_is_in_context(self):
        test_post = mixer.blend(Post, group=self.group)
        self.assertImageIsInContext(test_post, self.goust_user, self.path)

    def test_group_posts_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)

    def test_group_posts_pagination(self):
        self.assertPaginatorWorkDone(
            self.goust_user,
            self.path,
            Post.objects.
            filter(group=self.group).count())


class ProfileViewTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/profile.html'
        cls.user = mixer.blend(User)
        cls.path = reverse('posts:profile', args=(cls.user.username,))
        cls.goust_user = Client()
        mixer.cycle(POSTS_PER_PAGE).blend(Post, author=cls.user)

    def test_profile_status_code(self):
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_in_context(self):
        response = self.goust_user.get(self.path)
        user_from_context = self.get_field_from_context(response.context, User)
        self.assertEqual(user_from_context, self.user)

    def test_first_post_per_page(self):
        expected_post = mixer.blend(Post, author=self.user)
        response = self.goust_user.get(self.path)
        self.assertFirstPostMeetsExpectations(response, expected_post)

    def test_image_is_in_context(self):
        test_post = mixer.blend(Post, author=self.user)
        self.assertImageIsInContext(test_post, self.goust_user, self.path)

    def test_profile_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)

    def test_profile_pagination(self):
        self.assertPaginatorWorkDone(
            self.goust_user,
            self.path,
            Post.objects.filter(author=self.user).count())


class PostDetailViewTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/post_detail.html'
        cls.post = mixer.blend(Post)
        cls.goust_user = Client()
        cls.path = reverse('posts:post_detail', args=(cls.post.id,))

    def test_post_detail_status_code(self):
        response = self.goust_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_in_context(self):
        response = self.goust_user.get(self.path)
        post_from_context = self.get_field_from_context(response.context, Post)
        self.assertEqual(post_from_context, self.post)

    def test_image_is_in_context(self):
        self.assertImageIsInContext(self.post, self.goust_user, self.path)

    def test_post_detail_template(self):
        response = self.goust_user.get(self.path)
        self.assertTemplateUsed(response, self.template)


class CreatePostViewTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/create_post.html'
        cls.path = reverse('posts:post_create')
        cls.user = mixer.blend(User)
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = mixer.blend(Group)

    def test_create_post_status_code(self):
        response = self.authorized_user.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_template(self):
        response = self.authorized_user.get(self.path)
        self.assertTemplateUsed(response, self.template)

    def test_post_form_in_context(self):
        response = self.authorized_user.get(self.path)
        form_from_context = self.get_field_from_context(
            response.context, PostForm)
        self.assertIsInstance(form_from_context, PostForm)

    def test_form_show_correct_context(self):
        expected_value = PostForm()
        response = self.authorized_user.get(self.path)
        test_value = self.get_field_from_context(
            response.context, PostForm)
        for field, value in expected_value.fields.items():
            with self.subTest(field=field):
                self.assertIsInstance(test_value.fields[field], type(value))


class EditPostViewsTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = 'posts/create_post.html'
        cls.author = mixer.blend(User)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.post = mixer.blend(Post, author=cls.author)
        cls.path = reverse('posts:post_edit', args=(cls.post.id,))

    def test_edit_post_status_code(self):
        response = self.author_client.get(self.path)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_template(self):
        response = self.author_client.get(self.path)
        self.assertTemplateUsed(response, self.template)

    def test_post_form_in_context(self):
        expected_form = PostForm(instance=self.post)
        response = self.author_client.get(self.path)
        form_from_context = self.get_field_from_context(
            response.context, PostForm)
        self.assertIsInstance(form_from_context, PostForm)
        self.assertEqual(form_from_context.initial, expected_form.initial)

    def test_is_edit_in_context(self):
        response = self.author_client.get(self.path)
        self.assertEqual(response.context['is_edit'], True)


class ProfileFollowTest(FixtureForTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.goust_user = Client()
        cls.author = mixer.blend(User)
        cls.author_post = mixer.blend(Post, author=cls.author)
        cls.path_follow = reverse('posts:profile_follow', args=(cls.author.username,))
        cls.path_unfollow = reverse('posts:profile_unfollow', args=(cls.author.username,))

    def test_authorized_user_can_subscribe(self):
        follow_count = Follow.objects.count()
        self.authorized_user.get(self.path_follow)
        self.assertEqual(Follow.objects.count(),
                         follow_count + 1)
    
    def test_authorized_user_can_unsubscribe(self):
        self.authorized_user.get(self.path_follow)
        follow_count = Follow.objects.count()
        self.authorized_user.get(self.path_unfollow)
        self.assertEqual(Follow.objects.count(),
                         follow_count-1)
        
            
    def goust_user_cannot_subscribe(self):
        follow_count = Follow.objects.count()
        response = self.goust_user.get(self.path)
        self.assertEqual(Follow.objects.count(),
                         follow_count)
 
class FollowIndexTest(FixtureForTest):
    @classmethod
    def setUpClass(cls):
        cls.user = mixer.blend(User)
        cls.authorized_user= Client()
        cls.authorized_user.force_login(cls.user)
        cls.follow_author = mixer.blend(User)
        cls.another_author = mixer.blend(User)
        cls.path = reverse('posts:follow_index')
        follow = Follow(user= cls.user,
                        author = cls.follow_author)
        follow.save
        
        
    def new_post_appears_to_subscribed_users(self):
        exepted_post = mixer.blend(Post,
                                   author=self.follow_author)
        response = self.authorized_user.get(self.path)
        test_post = self.get_first_post_on_page(response)
        self.assertEqual(exepted_post,test_post)
    
    def new_post_does_not_appear_to_non_subscribed_users(self):
        exepted_post = mixer.blend(Post,
                                   author = self.another_author)
        response = self.authorized_user.get(self.path)
        test_post =self.get_first_post_on_page(response)
        self.assertNotEqual(exepted_post, test_post)
                  