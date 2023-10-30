import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_detail_page_contains_form(
        id_for_news, parametrized_client, form_in_context
):
    """Наличие формы на странице отдельной новости."""
    url = reverse('news:detail', args=(id_for_news))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context, (
        'Убедитесь, что для аутентифицированного пользователя на'
        ' странице новости передаётся форма, а для гостя нет.'
    )


def test_comments_order(client, id_for_news, two_comments):
    """Последовательности отображения комментариев - по убыванию."""
    detail_url = reverse('news:detail', args=(id_for_news))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created, (
        'Убедитесь, что комментарии к новости отсортированы по времени их'
        ' публикации, «от старых к новым».'
    )


def test_news_count(client, many_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'Убедитесь, что новостей на клавной странице не более,'
        f' чем {settings.NEWS_COUNT_ON_HOME_PAGE}.'
    )


def test_news_order(client, many_news):
    """Сортировка новостей на главной странице — по новизне."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, (
        'Убедитесь, что новости отсортированы по времени их'
        ' публикации, «от новых к старым».'
    )
