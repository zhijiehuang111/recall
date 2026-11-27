"""作答 note：`log` 記下缺口，`due` 把最近幾筆交還給 agent。"""

import json


def _log(vault, *events: dict) -> None:
    vault.log_path.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
    )


def _review(at: str, note: str | None = None, grade: str = "hard") -> dict:
    event: dict = {
        "event": "review",
        "card": "sql-having",
        "at": at,
        "grade": grade,
        "hints": 0,
    }
    if note is not None:
        event["note"] = note
    return event


def _notes(vault, today: str = "2026-12-31") -> list[str]:
    result = vault.due("--today", today)
    assert result.code == 0, result.stderr
    (card,) = [c for c in result.json()["cards"] if c["card"] == "sql-having"]
    return card["notes"]


def test_due_returns_the_last_three_notes_newest_first(ready_vault):
    ready_vault.add_card("sql-having")
    _log(
        ready_vault,
        _review("2026-11-01", "缺口一"),
        _review("2026-11-02", "缺口二"),
        _review("2026-11-03", "缺口三"),
        _review("2026-11-04", "缺口四"),
    )

    assert _notes(ready_vault) == ["缺口四", "缺口三", "缺口二"]


def test_due_ignores_notes_from_before_the_last_reset(ready_vault):
    ready_vault.add_card("sql-having")
    _log(
        ready_vault,
        _review("2026-11-01", "reset 前的缺口"),
        {"event": "reset", "card": "sql-having", "at": "2026-11-02"},
        _review("2026-11-03", "reset 後的缺口"),
    )

    assert _notes(ready_vault) == ["reset 後的缺口"]


def test_due_skips_reviews_without_a_note_or_with_a_blank_one(ready_vault):
    ready_vault.add_card("sql-having")
    _log(
        ready_vault,
        _review("2026-11-01", "最早的缺口"),
        _review("2026-11-02", "較早的缺口"),
        _review("2026-11-03", "上次的缺口"),
        _review("2026-11-04", grade="good"),
        _review("2026-11-05", "  "),
    )

    assert _notes(ready_vault) == ["上次的缺口", "較早的缺口", "最早的缺口"]


def test_due_returns_no_notes_for_cards_never_given_one(ready_vault):
    ready_vault.add_card("sql-having")

    assert _notes(ready_vault) == []

    ready_vault.review("sql-having", "good", "2026-11-01")
    assert _notes(ready_vault) == []


def test_a_note_does_not_change_when_the_card_is_due(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.add_card("cap-theorem")

    for card, note in (("sql-having", []), ("cap-theorem", ["--note", "漏了 P"])):
        for grade, at in (("good", "2026-11-01"), ("hard", "2026-11-02")):
            result = ready_vault.log(
                "review", card, "--grade", grade, "--hints", "0", "--at", at, *note
            )
            assert result.code == 0, result.stderr
            last_due = result.json()["due"]
        assert last_due == "2026-11-04"


def test_due_reports_a_note_that_is_not_a_string(ready_vault):
    ready_vault.add_card("sql-having")
    _log(ready_vault, _review("2026-11-01") | {"note": ["不是字串"]})

    result = ready_vault.due("--today", "2026-11-05")

    assert result.code != 0
    assert "第 1 行" in result.stderr
    assert "note" in result.stderr
