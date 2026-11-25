"""每日時間預算與排序：`due` 依 `daily_minutes` 決定加幾張新卡、以什麼順序考。"""


def _cards(result) -> list[str]:
    assert result.code == 0, result.stderr
    return [c["card"] for c in result.json()["cards"]]


def test_each_card_type_has_its_own_estimated_minutes(ready_vault):
    ready_vault.set_daily_minutes(60)
    ready_vault.add_card("sql-having", type="recall", created="2026-11-01")
    ready_vault.add_card("cap-theorem", type="explain", created="2026-11-02")
    ready_vault.add_card("lru-cache", type="build", created="2026-11-03")

    result = ready_vault.due("--today", "2026-11-10")

    assert result.code == 0, result.stderr
    assert {c["card"]: c["minutes"] for c in result.json()["cards"]} == {
        "sql-having": 3,
        "cap-theorem": 5,
        "lru-cache": 30,
    }


def test_new_cards_fill_the_budget_in_created_order_skipping_ones_that_do_not_fit(
    ready_vault,
):
    ready_vault.set_daily_minutes(10)
    ready_vault.add_card("tcp-handshake", type="recall", created="2026-11-01")  # 3
    ready_vault.add_card("lru-cache", type="build", created="2026-11-02")  # 30：放不下
    ready_vault.add_card("cap-theorem", type="explain", created="2026-11-03")  # 5
    ready_vault.add_card("acid", type="recall", created="2026-11-04")  # 3：超過 10

    result = ready_vault.due("--today", "2026-11-10")

    assert _cards(result) == ["tcp-handshake", "cap-theorem"]


def test_due_reviews_are_all_listed_even_over_budget_and_leave_no_room_for_new_cards(
    ready_vault,
):
    ready_vault.set_daily_minutes(5)
    for card in ("acid", "cap-theorem"):
        ready_vault.add_card(card, type="recall", created="2026-11-01")
        assert ready_vault.review(card, "good", "2026-11-03").code == 0
    ready_vault.add_card("sql-having", type="recall", created="2026-11-02")

    result = ready_vault.due("--today", "2026-11-10")

    assert sorted(_cards(result)) == ["acid", "cap-theorem"]


def test_due_reports_the_daily_budget_and_how_many_minutes_are_planned(ready_vault):
    ready_vault.set_daily_minutes(5)
    for card in ("acid", "cap-theorem"):
        ready_vault.add_card(card, type="recall", created="2026-11-01")
        assert ready_vault.review(card, "good", "2026-11-03").code == 0
    ready_vault.add_card("sql-having", type="recall", created="2026-11-02")

    over = ready_vault.due("--today", "2026-11-10")
    under = ready_vault.due("--today", "2026-11-03")

    assert over.json()["budget"] == {"daily_minutes": 5, "planned_minutes": 6}
    assert under.json()["budget"] == {"daily_minutes": 5, "planned_minutes": 3}


def test_order_is_again_or_hard_first_then_most_overdue_then_new_cards(ready_vault):
    ready_vault.set_daily_minutes(60)
    history = {
        "good-old": [("good", "2026-11-01")],  # 到期 11-02
        "good-recent": [("good", "2026-11-10")],  # 到期 11-11
        "recovered": [("again", "2026-11-01"), ("good", "2026-11-02")],  # 到期 11-08
        "hard-recent": [("hard", "2026-11-12")],  # 到期 11-13
        "again-old": [("again", "2026-11-08")],  # 到期 11-09
        "again-recent": [("again", "2026-11-15")],  # 到期 11-16
        # 同一天的再考不計入排程，所以最近一次仍算 Again；到期 11-15
        "retaken": [("again", "2026-11-14"), ("good", "2026-11-14")],
    }
    for card, reviews in history.items():
        ready_vault.add_card(card, created="2026-11-01")
        for grade, at in reviews:
            assert ready_vault.review(card, grade, at).code == 0
    ready_vault.add_card("brand-new", created="2026-11-01")

    result = ready_vault.due("--today", "2026-11-20")

    assert _cards(result) == [
        "again-old",
        "hard-recent",
        "retaken",
        "again-recent",
        "good-old",
        "recovered",
        "good-recent",
        "brand-new",
    ]


def test_due_rejects_a_daily_minutes_that_is_not_a_whole_number(ready_vault):
    (ready_vault.recall / "config.toml").write_text('daily_minutes = "30"\n')

    result = ready_vault.due("--today", "2026-11-10")

    assert result.code != 0
    assert result.stdout == ""
    assert "daily_minutes" in result.stderr
