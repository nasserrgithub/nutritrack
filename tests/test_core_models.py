def test_scaled_calories(sample_food_entry):
    expected = round((31.0 * 4 + 0.0 * 4 + 3.6 * 9) * 150 / 100, 2)
    assert sample_food_entry.scaled_calories() == expected


def test_scaled_protein(sample_food_entry):
    expected = round(31 * 150 / 100, 2)
    assert sample_food_entry.scaled_protein() == expected
