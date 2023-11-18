import pytest

from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus

from news.models import Comment
from news.forms import BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    comms_exp = Comment.objects.count()
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count


@pytest.mark.django_db
def test_comment_contains_forbidden_words(author_client, news):
    comms_exp = Comment.objects.count()
    for bad_word in BAD_WORDS:
        form_data = {'text': {bad_word}}
    url = reverse('news:detail', args=(news.pk,))
    response_anonymous = author_client.post(url, data=form_data)
    assert response_anonymous.status_code == HTTPStatus.OK
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, form_data, comment, url_to_comments, edit_url
):
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(
        admin_client, form_data, comment, edit_url
):
    response = admin_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    comms_exp = Comment.objects.count() - 1
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count


def test_other_user_cant_delete_comment(admin_client, delete_url):
    comms_exp = Comment.objects.count()
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count


def test_user_can_create_comment(author_client, detail_url, form_data, news,
                                 author, url_to_comments):
    comms_exp = Comment.objects.count() + 1
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author
