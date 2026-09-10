import pytest
import logging

from config.credentials import ADMIN_USERNAME, ADMIN_PASSWORD
from data.movies.movie_data import get_movie_payload

@pytest.fixture(autouse=True)
def log_test_name(request):
    """
    Фикстура, которая логирует название запускаемого теста.
    Автоматически применяется ко всем тестам в директории.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"\n{'#' * 60}")
    logger.info(f"# STARTING TEST: {request.node.name}")
    logger.info(f"{'#' * 60}\n")
    yield
    logger.info(f"\n{'#' * 60}")
    logger.info(f"# FINISHED TEST: {request.node.name}")
    logger.info(f"{'#' * 60}\n")

@pytest.fixture(scope="function")
def admin_authenticated_session(api_manager):
    """
    Логинит SUPER_ADMIN и кладёт Bearer-токен в session.headers.
    """
    login_data = {
        "email": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    }
    response = api_manager.auth_api.login_user(login_data)
    token = response.json()["accessToken"]
    api_manager.session.headers.update({"Authorization": f"Bearer {token}"})
    yield api_manager
    api_manager.session.headers.pop("Authorization", None)

@pytest.fixture(scope="function")
def created_movie(admin_authenticated_session):
    """
    Создаёт фильм перед тестом и удаляет после (teardown).
    """
    payload = get_movie_payload()
    movie = admin_authenticated_session.movie_api.create_movie(payload).json()
    yield movie
    try:
        admin_authenticated_session.movie_api.delete_movie(
            movie["id"], expected_status=200
        )
    except ValueError:
        pass


