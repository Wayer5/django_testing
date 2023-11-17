import pytest

from django.urls import reverse
from http import HTTPStatus

PAGINATION_CONST = 10
EXPECTED_COMMENTS = ['Старый комм', 'Новый комм']


@pytest.mark.django_db
def test_home_page_limit(client, create_news):
    for _ in range(15):
        create_news(title='Заголовок', text='Текст заметки')

    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK

    news_count = len(response.context['news_list'])
    assert news_count == PAGINATION_CONST


@pytest.mark.django_db
def test_home_page_order(client, create_news):
    create_news(title='Вторая новость', text='Текст второй новости')
    create_news(title='Первая новость', text='Текст первой новости')

    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK

    news_list = response.context['news_list']
    assert [n.title for n in news_list] == ['Вторая новость', 'Первая новость']


@pytest.mark.django_db
def test_news_detail_comments_order(
    client, create_comment, author, detail_url
):
    create_comment(text=EXPECTED_COMMENTS[0], author=author, news_id=1)
    create_comment(text=EXPECTED_COMMENTS[1], author=author, news_id=1)
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    comments = response.context.get('object').comment_set.all()
    assert [c.text for c in comments] == EXPECTED_COMMENTS


def test_comment_form_allowed_authenticated_user(author_client, create_news):
    news = create_news(title='Test News', text='Text')
    response = author_client.post(reverse(
        'news:detail', args=[news.pk]), data={'text': 'New'}
    )
    assert response.status_code == HTTPStatus.FOUND


def test_comment_form_forbidden_anonymous_user(client, create_news):
    news = create_news(title='Test News', text='Text')
    response = client.post(reverse(
        'news:detail', args=[news.pk]), data={'text': 'New Comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
