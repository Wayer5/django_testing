from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .mixin import TestMixinCreatNoteConstant, TestMixinNote

User = get_user_model()


class TestNotes(TestMixinCreatNoteConstant, TestMixinNote):

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None)
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_user(self):
        login_url = reverse('users:login')
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_author_note_(self):
        url = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
        )
        for name, kwargs in url:
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
