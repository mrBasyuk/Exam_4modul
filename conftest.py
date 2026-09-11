import logging
import requests
import pytest

from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
from config.credentials import ADMIN_USERNAME, ADMIN_PASSWORD
from data.movies.movie_data import get_movie_payload


def setup_logging():
    """
    Один раз настраивает логирование для всего прогона pytest.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(console_handler)
    return logger


setup_logging()


@pytest.fixture(autouse=True)
def log_test_name(request):
    """
    Перед/после каждого теста пишет его имя в лог.
    autouse=True — подключается сама, в тестах указывать не нужно.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"\n{'#' * 60}\n# STARTING TEST: {request.node.name}\n{'#' * 60}\n")
    yield
    logger.info(f"\n{'#' * 60}\n# FINISHED TEST: {request.node.name}\n{'#' * 60}\n")


@pytest.fixture(scope="session")
def session():
    """
    Одна HTTP-сессия на весь прогон pytest.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    ApiManager с общей session: auth_api, movie_api (и user_api, если есть).
    """
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    """
    Данные нового пользователя (ещё не зарегистрирован).
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
    Регистрирует test_user через API и добавляет id в словарь.
    """
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="function")
def admin_authenticated_session(api_manager):
    """
    Логин SUPER_ADMIN, Bearer в session.headers.
    После теста токен снимается.
    """
    response = api_manager.auth_api.login_user({
        "email": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    })
    token = response.json()["accessToken"]
    api_manager.session.headers.update({"Authorization": f"Bearer {token}"})
    yield api_manager
    api_manager.session.headers.pop("Authorization", None)


@pytest.fixture(scope="function")
def created_movie(admin_authenticated_session):
    """
    Создаёт фильм до теста и удаляет после (teardown).
    """
    movie = admin_authenticated_session.movie_api.create_movie(
        get_movie_payload()
    ).json()
    yield movie
    try:
        admin_authenticated_session.movie_api.delete_movie(
            movie["id"], expected_status=200
        )
    except ValueError:
        pass