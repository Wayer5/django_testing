from http import HTTPStatus

from django.contrib.auth import get_user_model
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .mixin import (TestMixinCreatNoteConstant, TestMixinNoteCreate,
                    TestMixinNoteEditDelete, TestMixinUpdateNoteConstant)

User = get_user_model()


class TestNoteCreation(TestMixinCreatNoteConstant, TestMixinNoteCreate):

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes = Note.objects.get()
        self.assertEqual(notes.title, self.NOTE_TITLE)
        self.assertEqual(notes.text, self.NOTE_TEXT)
        self.assertEqual(notes.slug, self.NOTE_SLUG)

    def test_anonymous_cant_create_note(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(note_count, 0)

    def test_unique_slug_field(self):
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author,
        )
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(response,
                             form='form', field='slug',
                             errors=f'{self.NOTE_SLUG}{WARNING}')

    def test_generate_slug_if_field_empty(self):
        self.form_data.pop('slug')
        expected_slug = slugify(self.form_data['title'])
        self.assertRedirects(
            self.author_client.post(self.url, data=self.form_data),
            self.success_url
        )
        self.author_client.post(self.url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(expected_slug, note.slug)


class TestNoteEditDelete(TestMixinCreatNoteConstant,
                         TestMixinUpdateNoteConstant,
                         TestMixinNoteEditDelete):

    def test_author_can_delete_note(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
