from http import HTTPStatus
from news.models import Comment
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, news_url, form_data):
    client.post(news_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author_client, author, news_url, news, form_data):
    response = author_client.post(news_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS}, еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news_url, delete_url):
    response = author_client.delete(delete_url)
    assertRedirects(response, news_url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, edit_url, form_data, comment, comments_url):
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url, form_data, comment):
    old_comment = comment.text
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment
