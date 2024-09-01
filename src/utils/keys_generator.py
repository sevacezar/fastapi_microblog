"""Module with additional other functions."""

import random
import string


def generate_key(length: int) -> str:
    """Function of user's keys generation."""
    characters = string.ascii_letters + string.digits
    key = ''.join(random.choice(characters) for _ in range(length))
    return key
