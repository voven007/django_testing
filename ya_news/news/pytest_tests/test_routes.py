from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (('news:home', None),
     ('news:detail', pytest.lazy_fixture('pk_news')),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None),
     )
)
@pytest.mark.django_db
def test_pages_availability_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('pk_comment')),
     ('news:delete', pytest.lazy_fixture('pk_comment')),),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, args, expected_status
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('pk_comment')),
     ('news:delete', pytest.lazy_fixture('pk_comment')),),
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
