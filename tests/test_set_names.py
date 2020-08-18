import re
import pytest
from ipset import create_target_set_name, create_temporary_set_name

# pylint: disable=redefined-outer-name; (for pytest fixtures)


def test_length(set_name: str) -> None:
    assert len(set_name) < 32


def test_country_code(set_name: str) -> None:
    assert "ZZ" in set_name


def test_characters(set_name: str) -> None:
    assert re.search("^[a-zA-Z0-9.-]+$", set_name)


@pytest.fixture(params=[create_target_set_name, create_temporary_set_name])
def set_name(request):  # type: ignore # currently no way to properly typehint fixtures
    return request.param("ZZ")
