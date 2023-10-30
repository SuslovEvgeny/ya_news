from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    """Проверка редиректов."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url), (
        'Убедитесь, что при запросе на удаление и редактирование,'
        'Незарегистрированный пользователь перенаправляется на регистрацию.'
    )


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_news')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    """Проверка доступности страниц."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'Убедитесь, что страница {url} доступна.'
    )


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, id_for_comment, expected_status
):
    """Проверка доступности для удаления и редактирования комментария."""
    url = reverse(name, args=(id_for_comment))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status, (
        'Убедитесь, что удаление и редактирование доступны только автору.'
    )
