from ..models import Post, Group, User, Follow
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class FollowTest(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.user_for_follow = User.objects.create_user(
            username='TestForFollow'
        )
        self.user_not_for_follow = User.objects.create_user(
            username='TestNotForFollow'
        )
        self.simple_user = Client()
        self.simple_user.force_login(self.user)
        self.follow_user = Client()
        self.follow_user.force_login(self.user_for_follow)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        self.post = Post.objects.create(
            text='Текст для тестового поста ',
            author=self.user_for_follow,
            group=self.group,
        )

    def test_comments(self):
        """Тестируем может ли не авторизированный и авторизированный
         пользователь оставлять комментарии"""
        response = self.guest_client.get(reverse(
            'add_comment', kwargs={'username': self.user_for_follow,
                                   'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.simple_user.get(reverse(
            'add_comment', kwargs={'username': self.user_for_follow,
                                   'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_add_unfollow(self):
        """Тестируем подписку и отписку на пользователя"""
        self.simple_user.get(reverse(
            'profile_follow', kwargs={'username': self.user_for_follow}
        ))
        follows = Follow.objects.filter(user=self.user.id)
        self.assertEqual(follows.count(), 1)
        self.simple_user.get(reverse(
            'profile_unfollow', kwargs={'username': self.user_for_follow}
        ))
        follows = Follow.objects.filter(user=self.user.id)
        self.assertEqual(follows.count(), 0)

    def test_follow_page(self):
        """Проверяем есть ли запись у пользователей подписанных
        и не подписанных на автора"""
        self.simple_user.get(reverse(
            'profile_follow', kwargs={'username': self.user_for_follow}
        ))
        response = self.simple_user.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 1)
        response = self.follow_user.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)
