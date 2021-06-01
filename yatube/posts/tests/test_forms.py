from django.test import Client, TestCase
from ..models import Post, Group, User
from django.urls import reverse


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        Group.objects.create(
            title='Тестовая группа 2',
            slug='test-2',
            description='Описание тестовой группы'
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка страницы создания поста"""
        group = Group.objects.first()
        form_data = {
            'text': 'Тестовый пост',
            'author': self.user,
            'group': group.pk
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, form_data['author'])
        self.assertEqual(post.group, group)

    def test_edit_post(self):
        """Проверка страницы изменения поста"""
        created_post = Post.objects.create(
            text='Текст тестового поста',
            author=self.user,
            group=Group.objects.first()
        )
        edited_group = Group.objects.last()
        edited_text = 'Измененный текст'
        form_data = {
            'text': edited_text,
            'author': self.user,
            'group': edited_group.pk,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': created_post.id,
            }),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.first()
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.author, form_data['author'])
        self.assertEqual(edited_post.group, edited_group)

        response = self.authorized_client.get(
            reverse('group', kwargs={
                'slug': Group.objects.first().slug
            }))

        self.assertEqual(len(response.context['page']), 0)
