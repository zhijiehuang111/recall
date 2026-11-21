def test_due_fails_clearly_when_vault_has_no_recall_dir(vault):
    vault.root.mkdir()

    result = vault.due()

    assert result.code != 0
    assert result.stdout == ""
    assert f"找不到 {vault.recall}/" in result.stderr


def test_due_lists_never_reviewed_cards_as_new(ready_vault):
    ready_vault.add_card("sql-having", type="recall", created="2026-11-02")
    ready_vault.add_card("cap-theorem", type="explain", created="2026-11-03")

    result = ready_vault.due("--today", "2026-11-10")

    assert result.code == 0, result.stderr
    assert sorted(result.json()["cards"], key=lambda c: c["card"]) == [
        {"card": "cap-theorem", "type": "explain", "kind": "new", "due": "2026-11-03"},
        {"card": "sql-having", "type": "recall", "kind": "new", "due": "2026-11-02"},
    ]


def test_due_reads_only_single_line_fields_and_skips_lines_it_does_not_understand(
    ready_vault,
):
    ready_vault.write_card(
        "tcp-handshake",
        "---\n"
        "title: >\n"
        "  type: build\n"
        "source:\n"
        "  - https://example.com/a\n"
        "  - notes/tcp.md\n"
        "tags: [net, interview]\n"
        'type: "explain"\n'
        "created: 2026-11-05\n"
        "---\n"
        "\n"
        "type: build\n",
    )

    result = ready_vault.due("--today", "2026-11-10")

    assert result.code == 0, result.stderr
    assert result.json()["cards"] == [
        {
            "card": "tcp-handshake",
            "type": "explain",
            "kind": "new",
            "due": "2026-11-05",
        },
    ]


def test_due_reports_which_log_line_is_broken(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log_path.write_text(
        '{"event": "review", "card": "sql-having", "at": "2026-11-03T08:00:00+08:00", "grade": "good", "hints": 0}\n'
        '{"event": "review", "card": "sql-having", "grade": "good", "hints": 0}\n'
    )

    result = ready_vault.due("--today", "2026-11-05")

    assert result.code != 0
    assert "第 2 行" in result.stderr


def test_due_ignores_event_types_it_does_not_know(ready_vault):
    ready_vault.add_card("sql-having")
    ready_vault.log_path.write_text(
        '{"event": "something-later", "card": "sql-having"}\n'
    )

    result = ready_vault.due("--today", "2026-11-05")

    assert result.code == 0, result.stderr
    assert [c["kind"] for c in result.json()["cards"]] == ["new"]
