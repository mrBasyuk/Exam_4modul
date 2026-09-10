import random
import uuid
from faker import Faker

faker = Faker()


class DataGenerator:
    """
    Генератор тестовых данных.
    """


    GENRE_IDS = [7, 8, 9, 10] # Стабильные id жанров, которые реально есть на стенде (GET /genres)

    @staticmethod
    def generate_random_movie_name():
        """Уникальное название фильма (текст + uuid)"""
        return f"{faker.sentence(nb_words=3).rstrip('.')} {uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_description():
        """Случайное описание фильма."""
        return faker.text(max_nb_chars=150)

    @staticmethod
    def generate_random_genre_id():
        """Случайный валидный genreId со стенда."""
        return random.choice(DataGenerator.GENRE_IDS)

    @staticmethod
    def generate_random_price():
        """Цена в допустимом диапазоне."""
        return random.randint(50, 1000)

    @staticmethod
    def generate_location():
        """Локация только MSK или SPB."""
        return random.choice(["MSK", "SPB"])

    @staticmethod
    def generate_random_boolean():
        """Случайное True/False."""
        return random.choice([True, False])

    @staticmethod
    def generate_random_image_url():
        """URL постера."""
        return f"https://example.com/posters/{uuid.uuid4().hex}.jpg"

    @staticmethod
    def generate_random_email():
        """Email для регистрации пользователя."""
        return faker.email(domain="example.ru")

    @staticmethod
    def generate_random_password():
        """Пароль для регистрации / логина."""
        return faker.password()

    @staticmethod
    def generate_random_name():
        """ФИО пользователя."""
        return faker.name()