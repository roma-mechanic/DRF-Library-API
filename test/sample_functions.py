from django.contrib.auth import get_user_model

from book.models import Book
from borrowing.models import Borrowing
from user.models import UserProfile


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Test Author",
        "cover": "hard",
        "inventory": 10,
        "daily_fee": 1.0,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {"email": "sample@sample.com", "password": "samplepassword"}
    defaults.update(params)
    user, created = get_user_model().objects.get_or_create(
        email=defaults["email"], defaults=defaults
    )
    if not created:
        user.set_password(defaults["password"])
        user.save()
    return user


def sample_user_profile_object(**params):
    defaults = {
        "user": sample_user(),
        "username": "sample_username",
    }
    defaults.update(params)
    user_profile, created = UserProfile.objects.get_or_create(
        user=defaults["user"], defaults=defaults
    )
    return user_profile


def sample_borrowing(**params):
    test_book_object = sample_book()

    defaults = {
        "borrow_date": "2023-12-27",
        "user": sample_user_profile_object(),
        "is_active": True,
    }
    defaults.update(params)
    borrowing = Borrowing.objects.create(**defaults)
    borrowing.book.set([test_book_object])
    return borrowing
