from http import HTTPStatus

from django.urls import reverse
import pytest
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
    """Пользователь может создавать комментарий."""
    url = reverse('news:detail', args=id_for_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1, (
        'Убедитесь, что комментарий создался.'
    )
    comment = Comment.objects.get()
    assert comment.text == form_data['text'], (
        'Убедитесь, что вы передали текст, который создался на странице.'
    )
    assert comment.news == news
    assert comment.author == author


def test_anonymous_user_cant_create_comment(client, form_data, id_for_news):
    """Гость не может создавать комментарий."""
    url = reverse('news:detail', args=id_for_news)
    client.post(url, data=form_data)
    Comment.objects.count()
    assert Comment.objects.count() == 0, (
        'Убедитесь, что комментарий может создать'
        ' только зарегистрированный пользователь.'
    )


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS,
)
def test_user_cant_use_bad_words(author_client, id_for_news, bad_word):
    """Плохи слова в комментариях."""
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    url = reverse('news:detail', args=id_for_news)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0, (
        'Убедитесь, что комментарий не может содержать'
        ' слова из запрещённого списка.'
    )


def test_author_can_edit_comment(
        author_client,
        form_data,
        id_for_comment,
        id_for_news,
        comment
):
    """Автор может редактировать комментарий."""
    edit_url = reverse('news:edit', args=id_for_comment)
    response = author_client.post(edit_url, data=form_data)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text'], (
        'Убедитесь, что автор комменатрия может его редактировать.'
    )


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        id_for_comment,
        comment
):
    """Другой пользователь не может редактировать комментарий автора."""
    edit_url = reverse('news:edit', args=id_for_comment)
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text, (
        'Убедитесь, что комментарий может редактировать'
        ' только автор комментария.'
    )


def test_author_can_delete_comment(author_client, id_for_comment, id_for_news):
    """Автор может удалять комментарий."""
    delete_url = reverse('news:delete', args=id_for_comment)
    response = author_client.delete(delete_url)
    news_url = reverse('news:detail', args=id_for_news)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0, (
        'Убедитесь, что автор комменатрия может его удалять.'
    )


def test_user_cant_delete_comment_of_another_user(
        admin_client,
        id_for_comment
):
    """Другой пользователь не может удалять комментарий автора."""
    delete_url = reverse('news:delete', args=id_for_comment)
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1, (
        'Убедитесь, что комментарий может удалять только автор комментария.'
    )
