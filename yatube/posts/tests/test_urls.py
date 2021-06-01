from django.test import TestCase, Client
from ..models import User, Group, Post
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):

    def setUp(self) -> None:
        # Создаем клиенты авторизированного и обычного пользователя
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='Test_user'
        )
        self.user_non_author = User.objects.create_user(
            username='Test_user_non_author'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.user_non_author)
        # Создаем объект группы и пост, для проверки страницы /group
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug'
        )
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group
        )
        self.all_user_pages = {'index': {},
                               'post': {'username': self.user.username,
                                        'post_id': self.post.id},
                               'profile': {'username': self.user.username},
                               'group': {'slug': self.group.slug}}
        self.authorized_user_pages = {'new_post': {},
                                      'post_edit': {
                                          'username': self.user.username,
                                          'post_id': self.post.id}}

    def test_for_all_user(self):
        for page, kwargs in self.all_user_pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_authorized_user(self):
        for page, kwargs in self.authorized_user_pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse(page,
                                                              kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_for_non_authorized_user_redirect(self):
        for page, kwargs in self.authorized_user_pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page, kwargs=kwargs))
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_templates_for_edit_page(self):
        response_authorized_client_author = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}))
        response_authorized_client_na = self.authorized_client_non_author.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}))
        response_non_authorized_client = self.guest_client.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}))
        self.assertTemplateUsed(response_authorized_client_author,
                                'create_and_edit_post.html')
        self.assertEqual(response_authorized_client_na.status_code,
                         HTTPStatus.FOUND)
        self.assertEqual(response_non_authorized_client.status_code,
                         HTTPStatus.FOUND)

    def test_404_if_page_not_found(self):
        """Проверяем возвращает ли сервер 404"""
        response = self.authorized_client.get('/some-one-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
