from ..models import Post, Group, User, Follow, Comment
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
            author=self.user,
            group=self.group,
        )

    def test_comments(self):
        """Тестируем может ли не авторизированный и авторизированный
         пользователь оставлять комментарии"""
        self.comment = Comment.objects.create(
            text='Какой то комментарий',
            author_id=int(self.user.id),
            post_id=int(self.post.id)
        )
        response = self.guest_client.get(reverse(
            'add_comment', kwargs={'username': self.user,
                                   'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.simple_user.get(reverse(
            'add_comment', kwargs={'username': self.user,
                                   'post_id': self.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_add_unfollow(self):
        pass
