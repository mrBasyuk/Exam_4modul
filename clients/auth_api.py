import logging
from custom_requester.custom_requester import CustomRequester


class AuthApi(CustomRequester):
    """
    Клиент auth-сервиса: регистрация, логин, логаут, refresh.

    Для Movies-тестов в основном login_user —
    чтобы получить Bearer-токен SUPER_ADMIN.
    """

    def __init__(self, session, base_url):
        """
        :param session: общая requests.Session
        :param base_url: https://auth.dev-cinescope.coconutqa.ru
        """
        super().__init__(session, base_url)
        self.login_endpoint = "/login"
        self.register_endpoint = "/register"
        self.logout_endpoint = "/logout"
        self.refresh_endpoint = "/refresh"
        self.logger = logging.getLogger(__name__)

    def login_user(self, login_data, expected_status=201, **kwargs):
        """
        POST /login — вход пользователя.
        """
        self.logger.info(f"Logging in user: {login_data.get('email')}")
        response = self.send_request(
            method="POST",
            endpoint=self.login_endpoint,
            data=login_data,
            expected_status=expected_status,
            **kwargs,
        )
        if response.status_code == 201:
            self.logger.info("Login successful")
        return response

    def register_user(self, user_data, expected_status=201, **kwargs):
        """
        POST /register — регистрация нового пользователя.
        """
        self.logger.info(f"Registering user: {user_data.get('email')}")
        response = self.send_request(
            method="POST",
            endpoint=self.register_endpoint,
            data=user_data,
            expected_status=expected_status,
            **kwargs,
        )
        if response.status_code == 201:
            self.logger.info(f"User registered successfully: {user_data.get('email')}")
        return response

    def logout_user(self, expected_status=200, **kwargs):
        """
        POST /logout — выход (инвалидация текущей сессии на сервере).
        """
        self.logger.info("Logging out user")
        response = self.send_request(
            method="POST",
            endpoint=self.logout_endpoint,
            expected_status=expected_status,
            **kwargs,
        )
        self.logger.info("Logout successful")
        return response

    def refresh_token(self, refresh_data, expected_status=200, **kwargs):
        """
        POST /refresh — обновление accessToken по refreshToken.
        """
        self.logger.info("Refreshing token")
        response = self.send_request(
            method="POST",
            endpoint=self.refresh_endpoint,
            data=refresh_data,
            expected_status=expected_status,
            **kwargs,
        )
        self.logger.info("Token refreshed successfully")
        return response