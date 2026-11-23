import json


def test_log_review_appends_exactly_one_review_event(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log_path.write_text(
        '{"event": "review", "card": "sql-having", "at": "2026-11-01T09:00:00+08:00", "grade": "good", "hints": 0}\n'
    )

    result = ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "hard",
        "--hints",
        "2",
        "--at",
        "2026-11-03T21:15:00+08:00",
    )

    assert result.code == 0, result.stderr
    lines = ready_vault.log_lines()
    assert len(lines) == 2
    assert json.loads(lines[1]) == {
        "event": "review",
        "card": "sql-having",
        "at": "2026-11-03T21:15:00+08:00",
        "grade": "hard",
        "hints": 2,
    }


def test_log_review_refuses_unknown_card_and_writes_nothing(ready_vault):
    ready_vault.add_card("sql-having")

    result = ready_vault.log(
        "review", "no-such-card", "--grade", "good", "--hints", "0"
    )

    assert result.code != 0
    assert "no-such-card" in result.stderr
    assert ready_vault.log_lines() == []


def test_log_review_refuses_invalid_grade_and_writes_nothing(ready_vault):
    ready_vault.add_card("sql-having")

    result = ready_vault.log(
        "review", "sql-having", "--grade", "perfect", "--hints", "0"
    )

    assert result.code != 0
    assert ready_vault.log_lines() == []


def test_log_review_starts_a_new_line_even_if_the_file_lacks_a_trailing_newline(
    ready_vault,
):
    ready_vault.add_card("sql-having")
    first = '{"event": "review", "card": "sql-having", "at": "2026-11-01T09:00:00+08:00", "grade": "good", "hints": 0}'
    ready_vault.log_path.write_text(first)

    result = ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-02T09:00:00+08:00",
    )

    assert result.code == 0, result.stderr
    lines = ready_vault.log_lines()
    assert lines[0] == first
    assert [json.loads(line)["at"] for line in lines] == [
        "2026-11-01T09:00:00+08:00",
        "2026-11-02T09:00:00+08:00",
    ]


def test_log_review_refuses_to_write_when_the_existing_log_is_corrupt(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log_path.write_text("not json\n")

    result = ready_vault.log("review", "sql-having", "--grade", "good", "--hints", "0")

    assert result.code != 0
    assert "第 1 行" in result.stderr
    assert ready_vault.log_lines() == ["not json"]


def test_log_review_defaults_at_to_now_with_a_timezone(ready_vault):
    from datetime import datetime

    ready_vault.add_card("sql-having")

    result = ready_vault.log("review", "sql-having", "--grade", "good", "--hints", "0")

    assert result.code == 0, result.stderr
    at = datetime.fromisoformat(json.loads(ready_vault.log_lines()[0])["at"])
    assert at.utcoffset() is not None
    assert abs((datetime.now().astimezone() - at).total_seconds()) < 60


def test_log_review_refuses_at_without_timezone(ready_vault):
    ready_vault.add_card("sql-having")

    result = ready_vault.log(
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        "--at",
        "2026-11-03T21:15:00",
    )

    assert result.code != 0
    assert ready_vault.log_lines() == []


def test_log_writes_to_the_vault_given_before_the_subcommand(ready_vault, tmp_path):
    ready_vault.add_card("sql-having")

    result = ready_vault.log(
        "--vault",
        str(ready_vault.root),
        "review",
        "sql-having",
        "--grade",
        "good",
        "--hints",
        "0",
        cwd=tmp_path,
    )

    assert result.code == 0, result.stderr
    assert len(ready_vault.log_lines()) == 1


def test_log_reset_appends_exactly_one_reset_event(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.review("sql-having", "good", "2026-11-01T09:00:00+08:00")

    result = ready_vault.reset("sql-having", "2026-11-03T21:15:00+08:00")

    assert result.code == 0, result.stderr
    assert result.json() == {"card": "sql-having", "due": None}
    lines = ready_vault.log_lines()
    assert len(lines) == 2
    assert json.loads(lines[1]) == {
        "event": "reset",
        "card": "sql-having",
        "at": "2026-11-03T21:15:00+08:00",
    }


def test_log_reset_refuses_unknown_card_and_writes_nothing(ready_vault):
    ready_vault.add_card("sql-having")

    result = ready_vault.log("reset", "no-such-card")

    assert result.code != 0
    assert "no-such-card" in result.stderr
    assert ready_vault.log_lines() == []


def test_log_reset_defaults_at_to_now_with_a_timezone(ready_vault):
    from datetime import datetime

    ready_vault.add_card("sql-having")

    result = ready_vault.log("reset", "sql-having")

    assert result.code == 0, result.stderr
    at = datetime.fromisoformat(json.loads(ready_vault.log_lines()[0])["at"])
    assert at.utcoffset() is not None
    assert abs((datetime.now().astimezone() - at).total_seconds()) < 60
