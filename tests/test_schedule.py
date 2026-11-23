"""排程（簡化 SM-2）：一串作答之後，卡片在哪天到期。

只看 `log` 輸出的下次到期日與 `due` 的清單；換演算法時只需調整預期日期。
"""

import json


def _due_after(vault, *reviews: tuple[str, str]) -> list[str]:
    """依序記下 (grade, 日期) 作答，回傳每次 `log` 輸出的下次到期日。"""
    dues = []
    for grade, at in reviews:
        result = vault.review("sql-having", grade, at)
        assert result.code == 0, result.stderr
        dues.append(result.json()["due"])
    return dues


def test_first_review_is_due_in_one_day_unless_easy(ready_vault):
    for card in ("a", "h", "g", "e"):
        ready_vault.add_card(card)

    at = "2026-11-03"
    assert ready_vault.review("a", "again", at).json()["due"] == "2026-11-04"
    assert ready_vault.review("h", "hard", at).json()["due"] == "2026-11-04"
    assert ready_vault.review("g", "good", at).json()["due"] == "2026-11-04"
    assert ready_vault.review("e", "easy", at).json()["due"] == "2026-11-07"


def test_good_reviews_stretch_the_interval_1_then_6_then_times_ease(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("good", "2026-11-02"),
        ("good", "2026-11-08"),
        ("good", "2026-11-23"),
    ) == [
        "2026-11-02",  # 1 天
        "2026-11-08",  # 6 天
        "2026-11-23",  # 6 × 2.5 = 15 天
        "2026-12-31",  # 15 × 2.5 = 37.5 → 38 天
    ]


def test_hard_grows_the_interval_by_1_2_and_lowers_ease(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("good", "2026-11-02"),
        ("hard", "2026-11-08"),
        ("good", "2026-11-15"),
    ) == [
        "2026-11-02",
        "2026-11-08",
        "2026-11-15",  # 6 × 1.2 = 7.2 → 7 天；ease 2.5 → 2.35
        "2026-12-01",  # 7 × 2.35 = 16.45 → 16 天
    ]


def test_easy_grows_the_interval_by_ease_times_1_3_and_raises_ease(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("good", "2026-11-02"),
        ("easy", "2026-11-08"),
        ("good", "2026-11-28"),
    ) == [
        "2026-11-02",
        "2026-11-08",
        "2026-11-28",  # 6 × 2.5 × 1.3 = 19.5 → 20 天；ease 2.5 → 2.65
        "2027-01-20",  # 20 × 2.65 = 53 天
    ]


def test_easy_on_the_second_review_is_never_sooner_than_good(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("easy", "2026-11-02"),
    ) == [
        "2026-11-02",
        "2026-11-10",  # Good 會給 6 天，Easy 再 × 1.3 = 7.8 → 8 天
    ]


def test_again_resets_the_interval_to_one_day_and_lowers_ease(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("good", "2026-11-02"),
        ("again", "2026-11-08"),
        ("good", "2026-11-09"),
        ("good", "2026-11-11"),
    ) == [
        "2026-11-02",
        "2026-11-08",
        "2026-11-09",  # 1 天；ease 2.5 → 2.3
        "2026-11-11",  # 1 × 2.3 = 2.3 → 2 天
        "2026-11-16",  # 2 × 2.3 = 4.6 → 5 天
    ]


def test_ease_never_drops_below_1_3(ready_vault):
    ready_vault.add_card("sql-having")
    agains = [("again", f"2026-11-0{day}") for day in range(1, 9)]

    dues = _due_after(
        ready_vault,
        *agains,  # 8 次 Again：ease 2.5 − 1.6 = 0.9，被擋在 1.3
        ("good", "2026-11-09"),
        ("good", "2026-11-11"),
        ("good", "2026-11-14"),
        ("good", "2026-11-18"),
        ("good", "2026-11-23"),
    )

    assert dues[8:] == [
        "2026-11-11",  # 1 × 1.3 = 1.3 → 1，但至少比上次多 1 天 → 2 天
        "2026-11-14",  # 2 × 1.3 = 2.6 → 3 天
        "2026-11-18",  # 3 × 1.3 = 3.9 → 4 天
        "2026-11-23",  # 4 × 1.3 = 5.2 → 5 天
        "2026-11-30",  # 5 × 1.3 = 6.5 → 7 天
    ]


def test_a_passing_review_always_lengthens_the_interval_by_at_least_a_day(
    ready_vault,
):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("hard", "2026-11-02"),
    ) == [
        "2026-11-02",
        "2026-11-04",  # 1 × 1.2 = 1.2 → 1，至少比上次多 1 天 → 2 天
    ]


def test_only_the_first_review_of_a_day_counts_toward_the_schedule(ready_vault):
    ready_vault.add_card("sql-having")

    dues = _due_after(
        ready_vault,
        ("again", "2026-11-03"),
        ("good", "2026-11-03"),  # 同一 Session 內 Lapse 後的再考
    )

    assert dues == ["2026-11-04", "2026-11-04"]
    assert [json.loads(line)["grade"] for line in ready_vault.log_lines()] == [
        "again",
        "good",
    ]
    cards = ready_vault.due("--today", "2026-11-04").json()["cards"]
    assert [(c["card"], c["due"]) for c in cards] == [("sql-having", "2026-11-04")]


def _listed(vault, today: str) -> dict[str, dict]:
    result = vault.due("--today", today)
    assert result.code == 0, result.stderr
    return {c["card"]: c for c in result.json()["cards"]}


def test_due_reports_lapses_and_flags_a_leech_on_the_third_lapse(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.add_card("cap-theorem")
    _due_after(
        ready_vault,
        ("again", "2026-11-01"),
        ("again", "2026-11-02"),
        ("again", "2026-11-02"),  # 同日再考，不算 Lapse
    )

    listed = _listed(ready_vault, "2026-11-03")
    assert (listed["sql-having"]["lapses"], listed["sql-having"]["leech"]) == (2, False)
    assert (listed["cap-theorem"]["lapses"], listed["cap-theorem"]["leech"]) == (
        0,
        False,
    )

    _due_after(ready_vault, ("again", "2026-11-03"))

    listed = _listed(ready_vault, "2026-11-04")
    assert (listed["sql-having"]["lapses"], listed["sql-having"]["leech"]) == (3, True)


def test_reset_starts_the_schedule_over_and_keeps_old_records(ready_vault):
    ready_vault.add_card("sql-having")
    _due_after(
        ready_vault,
        ("good", "2026-11-01"),
        ("again", "2026-11-02"),
        ("again", "2026-11-03"),
        ("again", "2026-11-04"),
    )
    assert _listed(ready_vault, "2026-11-05")["sql-having"]["leech"] is True

    reset = ready_vault.reset("sql-having", "2026-11-05")
    assert reset.code == 0, reset.stderr

    assert len(ready_vault.log_lines()) == 5
    listed = _listed(ready_vault, "2026-11-05")["sql-having"]
    assert (listed["kind"], listed["lapses"], listed["leech"]) == ("new", 0, False)

    # 同一天 reset 之後的作答照新卡算：Good 1 天、再 Good 6 天（ease 回到 2.5）
    assert _due_after(
        ready_vault,
        ("good", "2026-11-05"),
        ("good", "2026-11-06"),
        ("good", "2026-11-12"),
    ) == ["2026-11-06", "2026-11-12", "2026-11-27"]


def test_easy_after_easy_follows_interval_times_ease_times_1_3(ready_vault):
    ready_vault.add_card("sql-having")

    assert _due_after(
        ready_vault,
        ("easy", "2026-11-01"),
        ("easy", "2026-11-05"),
    ) == [
        "2026-11-05",  # 4 天；ease 2.5 → 2.65
        "2026-11-19",  # 4 × 2.65 × 1.3 = 13.78 → 14 天（比 Good 的 6 天長，取這個）
    ]
