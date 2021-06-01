from django.test import Client, TestCase
from ..models import Post, Group, User
from django.urls import reverse


class PostTest(TestCase):
    def setUp(self) -> None:
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug'
        )
        self.group_stranger = Group.objects.create(
            title='Тестовая группа 2',
            slug='test2-slug'
        )
        self.post = Post.objects.create(
            text='Текст тестового поста',
            author=self.user,
            group=self.group,
        )

    def test_index_page_post(self):
        """Тест контекста"""
        response_index = self.authorized_client.get(reverse('index'))
        response_group = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))
        self.assertEqual(
            response_index.context['page'][0],
            response_group.context['page'][0])

    def test_group2_page(self):
        """Проверка того что пост не попал в чужую группу"""
        self.assertEqual(Post.objects.filter(
            group=self.group_stranger).count(), 0)
