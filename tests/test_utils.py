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
