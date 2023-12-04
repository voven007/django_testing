from django.test import TestCase
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
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='test_note',
            author=cls.author)

    def test_note_in_list_in_author(self):
        """Заметка передается в список заметок"""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        assert self.notes in object_list

    def test_not_in_list_not_autor_note(self):
        """Заметки не путаются между пользователей"""
        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        assert self.notes not in object_list

    def test_in_notes(self):
        """Проверка заметок на создание и на не перепутанность"""
        users = (
            (self.author, True),
            (self.reader, False)
        )
        for user, status in users:
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            object_list = response.context['object_list']
            assert (self.notes in object_list) is status

    def test_client_has_form(self):
        """Проверка передачи форм"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,))
        )
        self.client.force_login(self.author)
        for page, args in urls:
            url = reverse(page, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
