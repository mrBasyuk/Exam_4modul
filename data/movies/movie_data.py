from utils.data_generator import DataGenerator


def get_movie_payload(**overrides):
    """
    Собирает тело запроса CreateMovieDto
    Через **overrides  определяем нужные поля, например:
        get_movie_payload(location="MSK", genreId=7)

    """
    payload = {
        "name": DataGenerator.generate_random_movie_name(),
        "imageUrl": DataGenerator.generate_random_image_url(),
        "price": DataGenerator.generate_random_price(),
        "description": DataGenerator.generate_description(),
        "location": DataGenerator.generate_location(),
        "published": True,
        "genreId": DataGenerator.generate_random_genre_id(),
    }
    payload.update(overrides)
    return payload


def get_update_movie_payload(**kwargs):
    """
    Тело для PATCH:
    """
    allowed = ("name", "description", "price", "location", "imageUrl", "published", "genreId")
    return {k: v for k, v in kwargs.items() if k in allowed and v is not None}