"""Topic 為 paused / done 時，考過的卡照常複習，從沒考過的卡 `due` 不列。"""

import pytest


@pytest.mark.parametrize("status", ["paused", "done"])
def test_inactive_topic_keeps_reviews_but_hides_new_cards(ready_vault, status):
    ready_vault.add_topic("oversell", status=status)
    ready_vault.add_topic_card("row-lock")
    ready_vault.add_topic_card("optimistic-lock")
    ready_vault.review("row-lock", "again", "2026-11-01")

    result = ready_vault.due("--today", "2026-11-02")

    assert result.code == 0, result.stderr
    assert [(c["card"], c["kind"]) for c in result.json()["cards"]] == [
        ("row-lock", "review"),
    ]


def test_active_topic_lists_its_new_cards(ready_vault):
    ready_vault.add_topic("oversell", status="active")
    ready_vault.add_topic_card("row-lock")

    result = ready_vault.due("--today", "2026-11-02")

    assert result.code == 0, result.stderr
    assert [c["card"] for c in result.json()["cards"]] == ["row-lock"]
