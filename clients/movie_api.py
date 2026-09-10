import logging
from custom_requester.custom_requester import CustomRequester


class MovieApi(CustomRequester):
    """
    Клиент для работы с эндпоинтами фильмов (MoviesController).

    Все методы — тонкие обёртки над CustomRequester.send_request:
    формируют URL, передают body/params и ожидаемый HTTP-статус.
    Сами assert’ы живут в тестах, здесь только HTTP-логика.
    """

    def __init__(self, session, base_url):
        """
        :param session: общая requests.Session (через неё уходит Authorization)
        :param base_url: https://api.dev-cinescope.coconutqa.ru
        """
        super().__init__(session, base_url)
        self.movies_endpoint = "/movies"
        self.logger = logging.getLogger(__name__)

    def get_movies(self, params=None, expected_status=200, **kwargs):
        """
        GET /movies — список фильмов с пагинацией и фильтрами.

        Роль: PUBLIC (токен не обязателен).
        Частые params: page, pageSize, locations, genreId, published, createdAt.
        """
        self.logger.info(f"Getting movies with params: {params}")
        return self.send_request(
            method="GET",
            endpoint=self.movies_endpoint,
            params=params,
            expected_status=expected_status,
            **kwargs,
        )

    def create_movie(self, movie_data, expected_status=201, **kwargs):
        """
        POST /movies — создание фильма.

        Роль: SUPER_ADMIN (нужен Bearer-токен).
        movie_data — CreateMovieDto (name, imageUrl, price, description,
        location, published, genreId).
        """
        self.logger.info(f"Creating movie: {movie_data.get('name')}")
        return self.send_request(
            method="POST",
            endpoint=self.movies_endpoint,
            data=movie_data,
            expected_status=expected_status,
            **kwargs,
        )

    def get_movie_by_id(self, movie_id, expected_status=200, **kwargs):
        """
        GET /movies/{id} — один фильм по идентификатору.

        Роль: PUBLIC(токен не обязателен).
        """
        self.logger.info(f"Getting movie by ID: {movie_id}")
        return self.send_request(
            method="GET",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            expected_status=expected_status,
            **kwargs,
        )

    def patch_movie(self, movie_id, movie_data, expected_status=200, **kwargs):
        """
        PATCH /movies/{id} — частичное редактирование фильма.

        Роль: SUPER_ADMIN.
        В body можно передать только изменившиеся поля.
        """
        self.logger.info(f"Patching movie {movie_id}")
        return self.send_request(
            method="PATCH",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            data=movie_data,
            expected_status=expected_status,
            **kwargs,
        )

    def delete_movie(self, movie_id, expected_status=200, **kwargs):
        """
        DELETE /movies/{id} — удаление фильма.

        Роль: SUPER_ADMIN.
        """
        self.logger.info(f"Deleting movie {movie_id}")
        return self.send_request(
            method="DELETE",
            endpoint=f"{self.movies_endpoint}/{movie_id}",
            expected_status=expected_status,
            **kwargs,
        )