from nutritrack.core.parsers import MacroAggregator


def test_total_calories(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 615.7
    assert ma.total_calories == expected


def test_total_protein(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 96.25
    assert ma.total_protein == expected


def test_total_carbs(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 1.65
    assert ma.total_carbs == expected


def test_total_fat(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 24.9
    assert ma.total_fat == expected


def test_remaining_calories(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 1184.3
    assert ma.remaining_macros()["calories"] == expected


def test_remaining_protein(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 53.75
    assert ma.remaining_macros()["protein"] == expected


def test_remaining_carbs(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 198.35
    assert ma.remaining_macros()["carbs"] == expected


def test_remaining_fat(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal, num_days=1)
    expected = 35.1
    assert ma.remaining_macros()["fat"] == expected


def test_top_foods_returns_most_common(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal)
    top = ma.top_foods(n=1)
    expected = "chicken breast"
    assert top[0][0] == expected  # appears twice vs boiled egg once


def test_top_foods_count(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal)
    top = ma.top_foods(n=1)
    expected = 2
    assert top[0][1] == expected  # appears twice vs boiled egg once


def test_entry_count(sample_food_entries, sample_macro_goal):
    ma = MacroAggregator(sample_food_entries, sample_macro_goal)
    expected = 3
    assert ma.entry_count == expected
