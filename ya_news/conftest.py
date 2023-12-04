import pytest
from django.urls import reverse
from news.models import News, Comment
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    newses = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return newses


@pytest.fixture
def pk_news(news):
    return news.pk,


@pytest.fixture
def comment(author, news):
    commented = Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий'
    )
    return commented


@pytest.fixture
def pk_comment(comment):
    return comment.pk,


@pytest.fixture
def home_url():
    home = reverse('news:home')
    return home


@pytest.fixture
def news_url(news, pk_news):
    newse = reverse('news:detail', args=(pk_news))
    return newse


@pytest.fixture
def delete_url(news, pk_comment):
    comments = reverse('news:delete', args=(pk_comment))
    return comments


@pytest.fixture
def edit_url(news_url, pk_comment):
    edit = reverse('news:edit', args=(pk_comment))
    return edit


@pytest.fixture
def comments_url(news_url):
    comments = news_url + '#comments'
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def create_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def create_comment(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
