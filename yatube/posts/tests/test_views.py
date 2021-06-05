import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from ..models import Post, Group, User, Comment, Follow
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
        self.user_for_follow = User.objects.create_user(
            username='TestForFollow'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follow_user = Client()
        self.follow_user.force_login(self.user_for_follow)
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

    def test_cache_index_page(self):
        response1 = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Текст для тестового поста ',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        response2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response1.content), len(response2.content))

    def test_comments_authorized_user(self):
        """Тестируем может ли авторизированный
         пользователь оставлять комментарии"""
        post = Post.objects.first()
        print(post)
        form_data = {
            'post': post,
            'author': self.user,
            'text': 'Текст тестового комментария',
        }
        self.authorized_client.post(
            reverse('add_comment', kwargs={
                'username': self.user.username,
                'post_id': post.id
            }),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        print(comment)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, form_data['post'])
        self.assertEqual(comment.author, form_data['author'])

    def test_comments_non_authorized_user(self):
        """Тестируем может ли не авторизированный
            пользователь оставлять комментарии"""
        post = Post.objects.first()
        form_data = {
            'post': post,
            'author': self.user,
            'text': 'Текст тестового комментария',
        }
        self.guest_client.post(
            reverse('add_comment', kwargs={
                'username': self.user.username,
                'post_id': post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertIsNone(Comment.objects.first())

    def test_follow(self):
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': self.user_for_follow}
        ))
        follows = Follow.objects.filter(user=self.user.id)
        self.assertEqual(follows.count(), 1)

    def test_unfollow(self):
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': self.user_for_follow}
        ))
        self.authorized_client.get(reverse(
            'profile_unfollow', kwargs={'username': self.user_for_follow}
        ))
        follows = Follow.objects.filter(user=self.user.id)
        self.assertEqual(follows.count(), 0)

    def test_follow_page(self):
        self.another_post = Post.objects.create(
            text='Текст проверки фолова ',
            author=self.user_for_follow,
            group=self.group,
        )
        """Проверяем есть ли запись у пользователей подписанных
        и не подписанных на автора"""
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': self.user_for_follow}
        ))
        response = self.authorized_client.get(reverse('follow_index'))
        print(response.context['page'][0])
        self.assertEqual(len(response.context['page']), 1)
        response = self.follow_user.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page']), 0)

