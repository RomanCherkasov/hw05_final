from django.test import TestCase
from ..models import Group, Post, User


class PostAndGroupStrMethodTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем объект группы
        cls.group = Group.objects.create(
            title='Заголовок группы'
        )
        # Создаем объект пользователя
        user = User.objects.create_user(
            username='Test_user'
        )
        # Создаем объект поста
        cls.post = Post.objects.create(
            text='Текст для теста который надо проверить',
            author=user,
        )

    def test_group_and_post_str_method(self):
        """Тестируем метод __str__ для группы и поста"""
        str_methods_and_data = {
            str(self.group): self.group.title,
            str(self.post): self.post.text[:15]
        }
        for str_methods, data in str_methods_and_data.items():
            with self.subTest(data=data):
                self.assertEqual(str_methods, data)
