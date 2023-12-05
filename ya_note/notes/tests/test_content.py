from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создание базы данных и пользователей"""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_author = Client()
        cls.auth_reader = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_reader.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='test_note',
            author=cls.author)

    def test_note_in_list_in_author(self):
        """Заметка передается в список заметок"""
        response = self.auth_author.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_not_in_list_not_autor_note(self):
        """Заметки не путаются между пользователей"""
        response = self.auth_reader.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_in_notes(self):
        """Проверка заметок на создание и на не перепутанность"""
        users = (
            (self.auth_author, True),
            (self.auth_reader, False)
        )
        for user, status in users:
            response = user.get(self.LIST_URL)
            object_list = self.notes in response.context['object_list']
            self.assertEqual(object_list, status)

    def test_client_has_form(self):
        """Проверка передачи форм"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,))
        )
        for page, args in urls:
            url = reverse(page, args=args)
            response = self.auth_author.get(url)
            self.assertIn('form', response.context)
