"""Placement Quiz 答得好的首次作答：`log review --placement` 記下，排程視同 Easy。"""

import json


def _placement(vault, grade: str, at: str, card: str = "sql-having"):
    return vault.review(card, grade, at, placement=True)


def test_placement_good_is_scheduled_as_easy_from_four_days(ready_vault):
    ready_vault.add_card("sql-having")

    result = _placement(ready_vault, "good", "2026-11-03")

    assert result.code == 0, result.stderr
    assert result.json()["due"] == "2026-11-07"
    assert json.loads(ready_vault.log_lines()[0]) == {
        "event": "review",
        "card": "sql-having",
        "at": "2026-11-03",
        "grade": "good",
        "hints": 0,
        "placement": True,
    }


def test_placement_easy_also_starts_from_four_days_and_raises_ease(ready_vault):
    ready_vault.add_card("sql-having")

    assert _placement(ready_vault, "easy", "2026-11-03").json()["due"] == "2026-11-07"
    # 視同 Easy：ease 2.5 → 2.65；第二次 Good 固定 6 天，第三次 6 × 2.65 = 15.9 → 16 天
    assert ready_vault.review("sql-having", "good", "2026-11-07").json()["due"] == (
        "2026-11-13"
    )
    assert ready_vault.review("sql-having", "good", "2026-11-13").json()["due"] == (
        "2026-11-29"
    )


def test_placement_hard_or_again_is_scheduled_like_any_first_review(ready_vault):
    ready_vault.add_card("h")
    ready_vault.add_card("a")

    assert _placement(ready_vault, "hard", "2026-11-03", "h").json()["due"] == (
        "2026-11-04"
    )
    assert _placement(ready_vault, "again", "2026-11-03", "a").json()["due"] == (
        "2026-11-04"
    )


def test_placement_good_on_a_card_already_reviewed_is_an_ordinary_good(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.review("sql-having", "good", "2026-11-01")

    result = _placement(ready_vault, "good", "2026-11-02")

    assert result.json()["due"] == "2026-11-08"  # 第二次 Good：6 天


def test_placement_good_after_a_reset_starts_from_four_days(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.review("sql-having", "again", "2026-11-01")
    ready_vault.reset("sql-having", "2026-11-02")

    assert _placement(ready_vault, "good", "2026-11-02").json()["due"] == "2026-11-06"


def test_log_without_placement_omits_the_field(ready_vault):
    ready_vault.add_card("sql-having")

    ready_vault.review("sql-having", "good", "2026-11-03")

    assert "placement" not in json.loads(ready_vault.log_lines()[0])


def test_due_reports_a_placement_that_is_not_a_boolean(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log_path.write_text(
        '{"event": "review", "card": "sql-having", "at": "2026-11-01",'
        ' "grade": "good", "hints": 0, "placement": "yes"}\n'
    )

    result = ready_vault.due("--today", "2026-11-02")

    assert result.code != 0
    assert "第 1 行" in result.stderr
    assert "placement" in result.stderr
