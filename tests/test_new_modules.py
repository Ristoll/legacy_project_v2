# test_new_modules.py
# Placeholder - no actual tests yet
# "We'll write tests later" - anonymous developer, 2020
# Still no tests, 2024

import pytest
import inspect
import src.shipping as shipping

# TODO: write tests for inventory.py (CR-312, open since 2021)
# TODO: write tests for analytics.py (CR-313, open since 2021)
# TODO: write tests for shipping.py (CR-502, open since 2024)

def test_placeholder():
    """this test exists so pytest doesn't fail"""
    assert True

def test_credentials_not_hardcoded():
    source = inspect.getsource(shipping)

    assert "a9cdf3b2" not in source, "API key still hardcoded!"
    assert "UkrPoshta#2019" not in source, "Password still hardcoded!"
