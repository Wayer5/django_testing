import pytest

from django.urls import reverse
from http import HTTPStatus

from news.models import Comment

PAGINATION_CONST = 10


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
    create_news(title='Вторая новость', text='Текст второй новости', id=2)
    create_news(title='Первая новость', text='Текст первой новости', id=1)

    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK

    news_list = response.context['news_list']
    assert [n.id for n in news_list] == [1, 2]


@pytest.mark.django_db
def test_news_detail_comments_order(
    client, create_comment, author, detail_url
):
    create_comment(text='текст', author=author, news_id=1, id=2)
    create_comment(text='текст', author=author, news_id=1, id=1)
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    comments = response.context.get('object').comment_set.all()
    assert [c.id for c in comments] == [1, 2]


def test_comment_form_allowed_authenticated_user(author_client, create_news):
    comms_exp = Comment.objects.count() + 1
    news = create_news(title='Test News', text='Text')
    response = author_client.post(reverse(
        'news:detail', args=[news.pk]), data={'text': 'New'}
    )
    assert response.status_code == HTTPStatus.FOUND
    comms_count = Comment.objects.count()
    assert comms_exp == comms_count


def test_comment_form_forbidden_anonymous_user(client, create_news):
    news = create_news(title='Test News', text='Text')
    response = client.post(reverse(
        'news:detail', args=[news.pk]), data={'text': 'New Comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
