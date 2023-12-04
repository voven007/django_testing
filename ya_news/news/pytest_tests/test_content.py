import pytest
from django.conf import settings


@pytest.mark.django_db
def test_news_count(create_news, client, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(create_news, client, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(create_comment, author_client, news_url, news):
    response = author_client.get(news_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[10].created


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_anonymous_client_has_no_form(user, status, news_url):
    response = user.get(news_url)
    result = 'form' in response.context
    assert result == status
