"""整條路徑：建卡 → due → log → due。此階段排程規則：任何作答後隔天到期。"""


def test_reviewed_card_leaves_todays_list_and_comes_back_the_next_day(ready_vault):
    ready_vault.add_card("sql-having", type="recall", created="2026-11-01")
    ready_vault.add_card("cap-theorem", type="explain", created="2026-11-02")

    before = ready_vault.due("--today", "2026-11-03").json()["cards"]
    assert {c["card"]: c["kind"] for c in before} == {
        "sql-having": "new",
        "cap-theorem": "new",
    }

    logged = ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-03T21:15:00+08:00",
    )
    assert logged.code == 0, logged.stderr

    same_day = ready_vault.due("--today", "2026-11-03").json()["cards"]
    assert [c["card"] for c in same_day] == ["cap-theorem"]

    next_day = ready_vault.due("--today", "2026-11-04").json()["cards"]
    assert {
        "card": "sql-having",
        "type": "recall",
        "kind": "review",
        "due": "2026-11-04",
    } in next_day
    assert {
        "card": "cap-theorem",
        "type": "explain",
        "kind": "new",
        "due": "2026-11-02",
    } in next_day


def test_overdue_card_stays_listed_with_its_original_due_date(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "again",
        "--hints",
        "3",
        "--at",
        "2026-11-03T08:00:00+08:00",
    )

    cards = ready_vault.due("--today", "2026-11-09").json()["cards"]

    assert cards == [
        {"card": "sql-having", "type": "recall", "kind": "review", "due": "2026-11-04"}
    ]


def test_latest_review_decides_the_due_date(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-03T08:00:00+08:00",
    )
    ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-04T08:00:00+08:00",
    )

    assert ready_vault.due("--today", "2026-11-04").json()["cards"] == []
    assert (
        ready_vault.due("--today", "2026-11-05").json()["cards"][0]["due"]
        == "2026-11-05"
    )


def test_log_reports_the_cards_next_due_date(ready_vault):
    ready_vault.add_card("sql-having")

    result = ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-03T21:15:00+08:00",
    )

    assert result.code == 0, result.stderr
    assert result.json() == {"card": "sql-having", "due": "2026-11-04"}


def test_due_can_run_against_a_vault_outside_the_current_directory(
    ready_vault, tmp_path
):
    ready_vault.add_card("sql-having")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = ready_vault.due(
        "--vault", str(ready_vault.root), "--today", "2026-11-03", cwd=elsewhere
    )

    assert result.code == 0, result.stderr
    assert [c["card"] for c in result.json()["cards"]] == ["sql-having"]
