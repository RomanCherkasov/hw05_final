from django.test import Client, TestCase, override_settings
from ..models import Post, Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

import shutil
import tempfile


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
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

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username='TestUser'
        )
        self.authorized_client.force_login(self.user)
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

    def test_create_post(self):
        """Проверка страницы создания поста"""

        group = Group.objects.first()
        form_data = {
            'text': 'Тестовый пост',
            'author': self.user,
            'group': group.pk,
            'image': self.uploaded,
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
        self.assertEqual(post.image.name, 'posts/small.gif')

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
            'image': self.uploaded,
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
        self.assertEqual(edited_post.image.name, 'posts/small.gif')
