from django.contrib.auth import get_user_model
from django.urls import reverse

from .mixin import TestMixinAuthorNoteReader, TestMixinCreatNoteConstant

User = get_user_model()


class TestContextNote(TestMixinCreatNoteConstant, TestMixinAuthorNoteReader):

    def test_context_note(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']

        self.assertTrue((self.note in object_list), True)

    def test_list_notes_user_dsnt_appear_notes_another(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        users = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, value in users:
            with self.subTest(client=client):
                response = client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertTrue(
                    (self.note in object_list) is value)

    def test_user_has_form(self):
        """На странице создания и редактирования заметки передаются формы."""
        for url, kwargs in (('notes:add', None),
                            ('notes:edit', {'slug': self.note.slug})):
            with self.subTest(url=url):
                url = reverse(url, kwargs=kwargs)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
