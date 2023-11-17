import pytest

from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def create_news(django_user_model):
    def create(**kwargs):
        return News.objects.create(**kwargs)

    return create


@pytest.fixture
def create_comment(django_user_model):
    def _create_comment(author, **kwargs):
        return Comment.objects.create(author=author, **kwargs)
    return _create_comment


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def forbidden_words():
    return ['редиска', 'негодяй']


@pytest.fixture
def home_url():
    home_url = reverse('news:home')
    return home_url


@pytest.fixture
def detail_url(news):
    detail_url = reverse('news:detail', args=(news.id,))
    return detail_url


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_to_comments(detail_url):
    return detail_url + '#comments'


@pytest.fixture
def login_url():
    return reverse('users:login')
