from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FIELDS = [
            {'field': 'title', 'verbose_name': 'Название группы',
                'help_text': 'Введите название группы'},
            {'field': 'slug', 'verbose_name': 'Адресс для страницы группы',
             'help_text': ('Введенный вами текст будет автоматически'
                           ' переведен в транслит и'
                           ' обрезан до 100 символов.')},
            {'field': 'description', 'verbose_name': 'Описание группы',
                'help_text': 'Введите описание группы'}
        ]

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@email.com',
            password='testpassword'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            description='Это тестовая группа',
        )

    def test_group_str(self):
        """Проверяем __str__ в Group"""
        self.assertEqual(str(self.group), 'Тестовая группа')

    def test_field_verbose_name_and_help_text(self):
        """Проверяем verbose_name и help_text во всех полях"""
        for field in self.FIELDS:
            with self.subTest(field=field):
                model_field = Group._meta.get_field(field['field'])
                self.assertEqual(model_field.verbose_name,
                                 field['verbose_name'])
                self.assertEqual(model_field.help_text, field['help_text'])


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FIELDS = [
            {'field': 'text', 'verbose_name': 'Текст поста',
                'help_text': 'Введите текст поста'},
            {'field': 'pub_date', 'verbose_name': 'Дата публикации'},
            {'field': 'author', 'verbose_name': 'Автор'},
            {'field': 'group', 'verbose_name': 'Группа',
                'help_text': 'Группа, к которой будет отнаситься пост'}
        ]

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@email.com',
            password='testpassword'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            description='Это тестовая группа'

        )
        self.post = Post.objects.create(
            text='Просто тестовый пост',
            author=self.user,
            group=self.group
        )

    def test_post_str(self):
        """Проверяем __str__  в Пост"""
        self.assertEqual(str(self.post), 'Просто тестовый')

    def test_field_verbose_name_and_help_text(self):
        """Проверяем verbose_name и help_text во всех полях"""
        for field in self.FIELDS:
            field_obj = Post._meta.get_field(field['field'])
            self.assertEqual(field_obj.verbose_name, field['verbose_name'])
            if 'help_text' in field:
                self.assertEqual(field_obj.help_text, field['help_text'])
