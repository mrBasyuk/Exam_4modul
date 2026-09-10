import pytest
from data.movies.movie_data import get_movie_payload, get_update_movie_payload
from utils.data_generator import DataGenerator
from config.credentials import ADMIN_USERNAME, ADMIN_PASSWORD


@pytest.mark.api
class TestMovies:
    """
    Набор тестов эндпоинтов Movies.
    """

    @pytest.mark.positive
    def test_get_movies_list_success(self, api_manager):
        """
        PUBLIC: список фильмов отдаёт корректную структуру и пагинацию.
        """
        response = api_manager.movie_api.get_movies(
            params={"page": 1, "pageSize": 5}
        )
        data = response.json()

        assert "movies" in data
        assert isinstance(data["movies"], list)
        assert "count" in data
        assert "page" in data
        assert "pageSize" in data
        assert "pageCount" in data
        assert data["page"] == 1
        assert data["pageSize"] == 5
        assert len(data["movies"]) <= 5
        if data["movies"]:
            m = data["movies"][0]
            assert "id" in m
            assert "name" in m
            assert "price" in m
            assert "location" in m
            assert "genre" in m

    @pytest.mark.positive
    def test_create_movie_success(self, admin_authenticated_session):
        """
        SUPER_ADMIN: создание фильма возвращает 201 и те же поля, что отправили.
        """
        payload = get_movie_payload()
        movie = admin_authenticated_session.movie_api.create_movie(payload).json()

        try:
            assert "id" in movie
            assert movie["name"] == payload["name"]
            assert movie["price"] == payload["price"]
            assert movie["location"] == payload["location"]
            assert movie["published"] == payload["published"]
            assert movie["genreId"] == payload["genreId"]
            assert "genre" in movie
            assert "createdAt" in movie
            assert "rating" in movie
        finally:
            admin_authenticated_session.movie_api.delete_movie(movie["id"])

    @pytest.mark.positive
    def test_get_movie_by_id_success(self, api_manager, created_movie):
        """
        PUBLIC: GET /movies/{id} возвращает ранее созданный фильм.
        """
        data = api_manager.movie_api.get_movie_by_id(created_movie["id"]).json()

        assert data["id"] == created_movie["id"]
        assert data["name"] == created_movie["name"]
        assert data["price"] == created_movie["price"]
        assert "reviews" in data

    @pytest.mark.positive
    def test_patch_movie_success(self, admin_authenticated_session, created_movie):
        """
        SUPER_ADMIN: PATCH меняет поля; проверяем и ответ, и повторный GET.
        """
        movie_id = created_movie["id"]
        new_name = DataGenerator.generate_random_movie_name()
        new_price = DataGenerator.generate_random_price()
        patch_data = get_update_movie_payload(name=new_name, price=new_price)

        updated = admin_authenticated_session.movie_api.patch_movie(
            movie_id, patch_data
        ).json()

        assert updated["id"] == movie_id
        assert updated["name"] == new_name
        assert updated["price"] == new_price

        actual = admin_authenticated_session.movie_api.get_movie_by_id(movie_id).json()
        assert actual["name"] == new_name
        assert actual["price"] == new_price

    @pytest.mark.positive
    def test_delete_movie_success(self, admin_authenticated_session):
        """
        SUPER_ADMIN: после DELETE фильм недоступен (GET → 404).
        """
        payload = get_movie_payload()
        movie_id = admin_authenticated_session.movie_api.create_movie(payload).json()["id"]

        admin_authenticated_session.movie_api.delete_movie(movie_id, expected_status=200)
        admin_authenticated_session.movie_api.get_movie_by_id(
            movie_id, expected_status=404
        )

    @pytest.mark.positive
    def test_get_movies_filter_by_location(self, admin_authenticated_session):
        """
        Фильтр locations.
        """
        payload = get_movie_payload(location="MSK", published=True)
        movie = admin_authenticated_session.movie_api.create_movie(payload).json()
        movie_id = movie["id"]

        try:
            data = admin_authenticated_session.movie_api.get_movies(
                params={
                    "locations": ["MSK"],
                    "page": 1,
                    "pageSize": 20,
                    "createdAt": "desc",
                }
            ).json()

            assert len(data["movies"]) >= 1
            for m in data["movies"]:
                assert m["location"] == "MSK"
            assert movie_id in [m["id"] for m in data["movies"]]
        finally:
            admin_authenticated_session.movie_api.delete_movie(movie_id)

    @pytest.mark.positive
    def test_get_movies_filter_by_genre_id(self, admin_authenticated_session):
        """
        Фильтр genreId.
        """
        genre_id = DataGenerator.generate_random_genre_id()
        payload = get_movie_payload(genreId=genre_id, published=True)
        movie = admin_authenticated_session.movie_api.create_movie(payload).json()
        movie_id = movie["id"]

        try:
            data = admin_authenticated_session.movie_api.get_movies(
                params={
                    "genreId": genre_id,
                    "page": 1,
                    "pageSize": 20,
                    "createdAt": "desc",
                }
            ).json()

            assert len(data["movies"]) >= 1
            for m in data["movies"]:
                assert m["genreId"] == genre_id
            assert movie_id in [m["id"] for m in data["movies"]]
        finally:
            admin_authenticated_session.movie_api.delete_movie(movie_id)

    @pytest.mark.positive
    def test_get_movies_with_pagination(self, api_manager):
        """
        Пагинация: pageSize.
        """
        page_size = 3
        data = api_manager.movie_api.get_movies(
            params={"page": 1, "pageSize": page_size}
        ).json()

        assert len(data["movies"]) <= page_size
        assert data["pageSize"] == page_size
        assert data["page"] == 1
        assert "count" in data
        assert "pageCount" in data

    # ========== НЕГАТИВНЫЕ ТЕСТЫ ==========

    @pytest.mark.negative
    def test_get_movie_by_invalid_id(self, api_manager):
        """Ищем фильм по не существующему id → 404."""
        api_manager.movie_api.get_movie_by_id(999_999_999, expected_status=404)

    @pytest.mark.negative
    def test_create_movie_without_required_field(self, admin_authenticated_session):
        """Создаем фильм без обязательного name → 400."""
        payload = get_movie_payload()
        del payload["name"]
        admin_authenticated_session.movie_api.create_movie(payload, expected_status=400)

    @pytest.mark.negative
    def test_create_movie_with_invalid_location(self, admin_authenticated_session):
        """Создаем фильм с location вне enum MSK/SPB → 400."""
        payload = get_movie_payload(location="INVALID")
        admin_authenticated_session.movie_api.create_movie(payload, expected_status=400)

    @pytest.mark.negative
    def test_create_movie_with_invalid_genre_id(self, admin_authenticated_session):
        """Создаем фильм с не существующим genreId → 400."""
        payload = get_movie_payload(genreId=999_999)
        admin_authenticated_session.movie_api.create_movie(payload, expected_status=400)

    @pytest.mark.negative
    def test_patch_movie_invalid_id(self, admin_authenticated_session):
        """PATCH несуществующего фильма → 404."""
        admin_authenticated_session.movie_api.patch_movie(
            999_999_999,
            get_update_movie_payload(name="New Name"),
            expected_status=404,
        )

    @pytest.mark.negative
    def test_delete_movie_invalid_id(self, admin_authenticated_session):
        """DELETE несуществующего фильма → 404."""
        admin_authenticated_session.movie_api.delete_movie(
            999_999_999, expected_status=404
        )

    @pytest.mark.negative
    def test_get_movies_with_invalid_page_size(self, api_manager):
        """pageSize больше максимума (20) → 400."""
        api_manager.movie_api.get_movies(
            params={"page": 1, "pageSize": 100},
            expected_status=400,
        )

    @pytest.mark.negative
    def test_create_movie_without_authorization(self, api_manager):
        """
        Создание без Bearer-токена → 401..
        """
        api_manager.session.headers.pop("Authorization", None)
        api_manager.movie_api.create_movie(get_movie_payload(), expected_status=401)