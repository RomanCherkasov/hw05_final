import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from ..models import Post, Group, User
from django.urls import reverse
from django import forms


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ViewsTests(TestCase):
    def setUp(self) -> None:
        """
        Создаем клиенты авторизированного и
        не авторизированного пользователя
        """
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создадим группу для теста
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug'
        )
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        # Создаем записи в бд
        self.post = Post.objects.create(
            text='Текст для тестового поста ',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def test_pages_use_correct_template(self):
        """Проверяем что отдаются корректные Templates"""
        templates_page_names = {
            'index.html': [reverse('index')],
            'post.html': [reverse(
                'post', kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id})],
            'profile.html': [reverse(
                'profile', kwargs={
                    'username': self.user.username})],
            'group.html': [reverse('group', kwargs={'slug': self.group.slug})],
            'create_and_edit_post.html':
                [reverse('new_post'),
                 reverse('post_edit',
                         kwargs={
                             'username': self.user.username,
                             'post_id': self.post.id})],
        }
        for template, reverse_names in templates_page_names.items():
            for reverse_name in reverse_names:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_request_context_index_page(self):
        """Проверка контекста страницы главная"""
        response = self.authorized_client.get(reverse('index'))
        context_page = response.context['page'][0]
        self.post_check(context_page)
        self.assertEqual(context_page.image,
                         self.post.image)

    def test_request_context_group_page(self):
        """Проверка контекста страницы группы"""
        response = self.authorized_client.get(
            reverse('group', kwargs={
                'slug': self.group.slug,
            }))
        context_group = response.context['group']
        context_group_img = response.context['page'][0].image
        self.assertEqual(context_group_img, self.post.image)
        self.assertEqual(context_group.slug, self.post.group.slug)

    def test_request_context_new_page(self):
        """Проверка контекста страницы создания поста"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertFalse(response.context['is_edit'])

    def post_check(self, some_post):
        """Проверяем отданный пост на корректность"""
        self.assertEqual(self.post.text, some_post.text)
        self.assertEqual(self.post.author, some_post.author)
        self.assertEqual(self.post.group, some_post.group)
        self.assertEqual(self.post.pub_date, some_post.pub_date)
        self.assertEqual(self.post.image, some_post.image)

    def test_request_context_post_edit(self):
        """Проверка контекста страницы редактирования"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)
            self.assertTrue(response.context['is_edit'])

    def test_request_context_profile_page(self):
        """Проверка контекста страницы профиля"""
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': self.user.username, }))
        self.post_check(response.context['page'][0])
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count_post'],
            Post.objects.filter(author__username=self.user.username).count())
        self.assertEqual(response.context['page'][0].image,
                         self.post.image)

    def test_request_context_post_page(self):
        """Проверка контекста страницы поста"""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        self.post_check(response.context['post'])
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count_post'],
            Post.objects.filter(author__username=self.user.username).count())
        self.assertEqual(response.context['post'].image,
                         self.post.image)
