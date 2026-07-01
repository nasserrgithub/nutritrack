import pytest
from nutritrack.core.exceptions import InvalidMacroError
from nutritrack.core.utils import calculate_calories


def test_calculate_calories_no_fiber_argument():
    result = calculate_calories(protein_g=10, carbs_g=20, fat_g=5)
    assert result == (10 * 4) + (20 * 4) + (5 * 9)


def test_calculate_calories_explicit_zero_fiber():
    result = calculate_calories(protein_g=10, carbs_g=20, fat_g=5, fiber_g=0.0)
    assert result == (10 * 4) + (20 * 4) + (5 * 9)


def test_calculate_calories_with_real_fiber():
    result = calculate_calories(protein_g=10, carbs_g=20, fat_g=5, fiber_g=3.0)
    # fiber is subtracted from carbs before the 4 kcal/g multiplication
    expected_net_carbs = 20 - 3.0
    assert result == (10 * 4) + (expected_net_carbs * 4) + (5 * 9)


@pytest.mark.parametrize(
    "protein_g, carbs_g, fat_g, fiber_g",
    [
        (-10, 20, 5, None),  # negative protein
        (10, -20, 5, None),  # negative carbs
        (10, 20, -5, None),  # negative fat
        (10, 20, 5, -2.0),  # negative fiber
    ],
)
def test_calculate_calories_negative_macro_raises(protein_g, carbs_g, fat_g, fiber_g):
    with pytest.raises(InvalidMacroError):
        calculate_calories(
            protein_g=protein_g, carbs_g=carbs_g, fat_g=fat_g, fiber_g=fiber_g
        )
