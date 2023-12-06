from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from notes.forms import WARNING
from pytest_django.asserts import assertRedirects
from pytils.translit import slugify
User = get_user_model()


class TestNoteCreation(TestCase):
    ADD_NOTE = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.form_data = {
            'title': 'Новая Заметка',
            'text': 'Новый текст',
            'slug': 'new_slug'
        }

    def test_user_can_create_note(self):
        response = self.auth_author.post(self.ADD_NOTE, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.ADD_NOTE, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_NOTE}'
        assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        self.auth_author.post(self.ADD_NOTE, data=self.form_data)
        response = self.auth_author.post(self.ADD_NOTE, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.form_data['slug'] + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_author.post(self.ADD_NOTE, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_reader = Client()
        cls.auth_author = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.auth_author.force_login(cls.author)
        cls.notes = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='test_note',
            author=cls.author)
        cls.form_data = {
            'title': 'Новая Заметка',
            'text': 'Новый текст',
            'slug': 'new_slug'
        }
        cls.url_edit = reverse('notes:edit', args=(cls.notes.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.notes.slug,))

    def test_author_can_edit_note(self):
        response = self.auth_author.post(self.url_edit, self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.auth_reader.post(self.url_edit, self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        note_from_db = Note.objects.get(slug=self.notes.slug)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.auth_author.post(self.url_delete)
        assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.auth_reader.post(self.url_delete)
        assert response.status_code == HTTPStatus.NOT_FOUND
        self.assertEqual(Note.objects.count(), 1)
