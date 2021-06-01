from django.test import Client, TestCase
from ..models import Post, Group, User
from django.urls import reverse


class PaginatorTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        self.all_pages = [
            ('index', {}, 10, None),
            ('index', {'page': 2}, 5, None),
            ('group', {}, 10, {'slug': self.group.slug}),
            ('group', {'page': 2}, 5, {'slug': self.group.slug}),
            ('profile', {}, 10, {'username': self.user.username}),
            ('profile', {'page': 2}, 5, {'username': self.user.username})
        ]

    def test_all_paginator_pages(self):
        for _ in range(15):
            Post.objects.create(
                text=f'{_}Текст для тестового поста',
                author=self.user,
                group=self.group,)

        for page, page_param, count, kwargs in self.all_pages:
            with self.subTest(page=page + str(page_param.get('page', 1))):
                response = self.authorized_client.get(
                    reverse(page, kwargs=kwargs), page_param)
                self.assertEqual(len(response.context['page']), count)
