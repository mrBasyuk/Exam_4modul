from clients.auth_api import AuthApi
from clients.movie_api import MovieApi
from config.base_urls import BASE_URL, AUTH_BASE_URL


class ApiManager:
    """
    Единая точка доступа ко всем API-клиентам проекта.

    Хранит одну HTTP-сессию и раздаёт её AuthApi / MovieApi.
    В тестах обращаемся так: api_manager.movie_api.create_movie(...).
    """

    def __init__(self, session):
        """
        :param session: requests.Session на весь прогон pytest
        """
        self.session = session
        self.auth_api = AuthApi(session, AUTH_BASE_URL)
        self.movie_api = MovieApi(session, BASE_URL)