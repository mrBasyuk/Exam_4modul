import json
import logging
import os
import time
import requests


class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.session.headers.update(self.base_headers)
        self.logger = logging.getLogger(__name__)

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True, **kwargs):
        """
        Отправляет запрос и логирует его.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, PATCH)
            endpoint: эндпоинт API
            data: тело запроса (JSON)
            params: параметры запроса (query params)
            expected_status: ожидаемый статус код
            need_logging: логировать ли запрос/ответ
            **kwargs: дополнительные параметры для requests
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        # Логируем запрос ДО отправки
        if need_logging:
            self.log_request(method, url, data, params, kwargs)

        response = self.session.request(method, url, json=data, params=params, **kwargs)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Логируем ответ ПОСЛЕ получения
        if need_logging:
            self.log_response(response, elapsed_ms)

        # Проверяем статус код
        if response.status_code != expected_status:
            error_msg = (
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}\n"
                f"Response body: {response.text[:500]}"  # Показываем первые 500 символов
            )
            raise ValueError(error_msg)

        return response

    def log_request(self, method, url, data=None, params=None, kwargs=None):
        """
        Логирует исходящий запрос в формате curl.
        """
        try:
            GREEN = '\033[32m'
            RESET = '\033[0m'

            # Получаем имя теста
            full_test_name = os.environ.get('PYTEST_CURRENT_TEST', 'Unknown Test')
            test_name = full_test_name.replace(' (call)', '') if full_test_name else 'Unknown Test'

            # Формируем curl команду
            curl_parts = [f"curl -X {method} '{url}'"]

            # Добавляем заголовки
            headers = self.session.headers.copy()
            if kwargs and 'headers' in kwargs:
                headers.update(kwargs['headers'])

            for key, value in headers.items():
                if key not in ['Content-Length', 'Accept-Encoding']:  # Пропускаем технические заголовки
                    curl_parts.append(f"-H '{key}: {value}'")

            # Добавляем параметры
            if params:
                param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
                curl_parts[0] = f"curl -X {method} '{url}?{param_str}'"

            # Добавляем тело запроса
            if data:
                data_str = json.dumps(data, ensure_ascii=False)
                curl_parts.append(f"-d '{data_str}'")

            curl_command = " \\\n  ".join(curl_parts)

            # Логируем запрос
            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(f"{GREEN}{test_name}{RESET}")
            self.logger.info(curl_command)
            self.logger.info(f"{'=' * 80}\n")

        except Exception as e:
            self.logger.error(f"Failed to log request: {e}")

    def log_response(self, response, elapsed_ms):
        """
        Логирует полученный ответ.
        """
        try:
            GREEN = '\033[32m'
            RED = '\033[31m'
            YELLOW = '\033[33m'
            RESET = '\033[0m'

            status = response.status_code
            is_success = 200 <= status < 300

            # Пытаемся красиво отформатировать JSON
            try:
                response_data = json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                response_data = response.text

            # Определяем цвет для статуса
            status_color = GREEN if is_success else RED

            # Логируем ответ
            self.logger.info(f"{'=' * 40} RESPONSE {'=' * 40}")
            self.logger.info(
                f"STATUS: {status_color}{status}{RESET} "
                f"({YELLOW}{elapsed_ms} ms{RESET})"
            )

            # Если есть тело ответа, показываем его
            if response_data and response_data not in ['', 'null']:
                # Обрезаем очень длинные ответы
                if len(response_data) > 2000:
                    response_data = response_data[:2000] + "\n... (truncated)"
                self.logger.info(f"BODY:\n{response_data}")

            self.logger.info(f"{'=' * 80}\n")

        except Exception as e:
            self.logger.error(f"Failed to log response: {e}")

    def update_session_headers(self, headers: dict):
        """Обновляет заголовки сессии."""
        self.session.headers.update(headers)
        self.logger.info(f"Headers updated: {headers}")

    def _reset_headers(self):
        """Сбрасывает заголовки сессии к базовым значениям."""
        self.session.headers.clear()
        self.session.headers.update(self.headers)
        self.logger.info("Headers reset to default")