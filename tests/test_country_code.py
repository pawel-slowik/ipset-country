import pytest
from ipset import normalize_country_code


@pytest.mark.parametrize(
    "input_country_code,expected_country_code",
    (
        ("pl", "pl"),
        ("PL", "pl"),
        ("pL", "pl"),
    ),
)
def test_valid_country_code(
        input_country_code: str,
        expected_country_code: str,
) -> None:
    assert normalize_country_code(input_country_code) == expected_country_code


@pytest.mark.parametrize(
    "input_country_code",
    (
        (" pl"),
        ("POL"),
        ("pł"),
        ("𝗉l"), # Unicode MATHEMATICAL SANS-SERIF ITALIC SMALL P
        ("p⁠l"), # Unicode word joiner
    ),
)
def test_invalid_country_code(
        input_country_code: str,
) -> None:
    with pytest.raises(ValueError):
        normalize_country_code(input_country_code)
