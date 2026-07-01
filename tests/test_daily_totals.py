from datetime import date
from nutritrack.core.parsers import get_daily_totals


def test_get_daily_totals_groups_by_date(multi_day_food_entries):
    totals = list(get_daily_totals(multi_day_food_entries))
    assert len(totals) == 2  # two distinct dates -> two groups


def test_get_daily_totals_entry_count_per_day(multi_day_food_entries):
    totals = list(get_daily_totals(multi_day_food_entries))

    for t in totals:
        if t["date"] == date.today():
            assert t["entry_count"] == 1
        else:
            assert t["entry_count"] == 2


def test_get_daily_totals_empty_list():
    totals = list(get_daily_totals([]))
    assert totals == []
