from django.test import Client, TestCase
from ..models import Post, Group, User
from django.urls import reverse
from django import forms


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
        # Создаем записи в бд
        self.post = Post.objects.create(
            text='Текст для тестового поста ',
            author=self.user,
            group=self.group
        )

    def test_pages_use_correct_template(self):
        # Проверяем что отдаются корректные Templates
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
        # Проверяем index page context
        response = self.authorized_client.get(reverse('index'))
        context_page = response.context['page'][0]
        self.post_check(context_page)

    def test_request_context_group_page(self):
        # Проверяем group page context
        response = self.authorized_client.get(
            reverse('group', kwargs={
                'slug': self.group.slug,
            }))
        context_group = response.context['group']
        self.assertEqual(context_group.slug, self.post.group.slug)

    def test_request_context_new_page(self):
        # Проверяем new page context
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

    def test_request_context_post_page(self):
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        self.post_check(response.context['post'])
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count_post'],
            Post.objects.filter(author__username=self.user.username).count())
