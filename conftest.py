import logging
import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator

def setup_logging():
    """Настройка логирования для тестов"""
    # Создаём логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Удаляем существующие хендлеры, чтобы избежать дублирования
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создаём консольный хендлер с цветным форматированием
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Формат для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Настраиваем логирование при старте
setup_logging()


@pytest.fixture(scope="session")
def session():
    """
    Одна HTTP-сессия на весь прогон pytest.
    Через неё идут все запросы; в неё же кладётся Authorization после логина.
    В конце прогона сессия закрывается.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    ApiManager с общей session: доступ к auth_api и movie_api из любого теста.
    """
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    """
    Словарь данных нового пользователя (ещё не зарегистрирован).
    scope=function — у каждого теста свои email/password.
    """
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"],
    }


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    """
    Регистрирует test_user через API и дописывает id в словарь.
    Нужна auth-тестам (логин уже существующего пользователя).
    """
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user