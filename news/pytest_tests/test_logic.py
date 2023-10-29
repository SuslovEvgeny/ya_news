from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
        author_client,
        author,
        form_data,
        id_for_news,
        news
):
    url = reverse('news:detail', args=id_for_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_anonymous_user_cant_create_comment(client, form_data, id_for_news):
    url = reverse('news:detail', args=id_for_news)
    client.post(url, data=form_data)
    Comment.objects.count()
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, id_for_news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=id_for_news)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client,
        form_data,
        id_for_comment,
        id_for_news,
        comment
):
    edit_url = reverse('news:edit', args=id_for_comment)
    response = author_client.post(edit_url, data=form_data)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        id_for_comment,
        comment
):
    edit_url = reverse('news:edit', args=id_for_comment)
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, id_for_comment, id_for_news):
    delete_url = reverse('news:delete', args=id_for_comment)
    response = author_client.delete(delete_url)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client,
        id_for_comment
):
    delete_url = reverse('news:delete', args=id_for_comment)
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
