"""Capstone Card 等同 Topic 其他卡都有非 Again 作答（reset 以來）才由 `due` 以新卡列出。"""


def _capstone(vault, card_id: str = "oversell-capstone", topic: str = "oversell"):
    vault.add_card(card_id, extra=f"topic: {topic}\ncapstone: true\n")


def _listed(vault, today: str) -> list[str]:
    result = vault.due("--today", today)
    assert result.code == 0, result.stderr
    return [c["card"] for c in result.json()["cards"]]


def test_capstone_is_held_back_while_a_topic_card_was_never_reviewed(ready_vault):
    _capstone(ready_vault)
    ready_vault.add_topic_card("row-lock")

    assert _listed(ready_vault, "2026-11-05") == ["row-lock"]


def test_capstone_is_held_back_while_a_topic_card_has_only_again_reviews(
    ready_vault,
):
    _capstone(ready_vault)
    ready_vault.add_topic_card("row-lock")
    ready_vault.review("row-lock", "again", "2026-11-01")

    assert _listed(ready_vault, "2026-11-02") == ["row-lock"]


def test_capstone_is_listed_once_every_topic_card_has_a_non_again_review(
    ready_vault,
):
    _capstone(ready_vault)
    ready_vault.add_topic_card("row-lock")
    ready_vault.add_topic_card("optimistic-lock")
    ready_vault.review("row-lock", "again", "2026-11-01")
    ready_vault.review("row-lock", "hard", "2026-11-02")
    ready_vault.review("optimistic-lock", "good", "2026-11-02")

    assert "oversell-capstone" in _listed(ready_vault, "2026-11-03")


def test_a_non_again_review_before_a_reset_no_longer_unlocks_the_capstone(
    ready_vault,
):
    _capstone(ready_vault)
    ready_vault.add_topic_card("row-lock")
    ready_vault.review("row-lock", "good", "2026-11-01")
    ready_vault.reset("row-lock", "2026-11-02")

    assert _listed(ready_vault, "2026-11-03") == ["row-lock"]


def test_capstone_of_a_topic_with_no_other_cards_is_listed(ready_vault):
    _capstone(ready_vault)

    assert _listed(ready_vault, "2026-11-05") == ["oversell-capstone"]


def test_cards_of_other_topics_do_not_hold_back_the_capstone(ready_vault):
    _capstone(ready_vault)
    ready_vault.add_topic_card("cap-theorem", topic="distributed")
    ready_vault.add_card("sql-having")

    assert "oversell-capstone" in _listed(ready_vault, "2026-11-05")


def test_a_reviewed_capstone_stays_due_after_a_new_topic_card_is_added(
    ready_vault,
):
    _capstone(ready_vault)
    ready_vault.review("oversell-capstone", "hard", "2026-11-01")
    ready_vault.add_topic_card("row-lock")

    result = ready_vault.due("--today", "2026-11-02")

    assert result.code == 0, result.stderr
    assert [(c["card"], c["kind"]) for c in result.json()["cards"]] == [
        ("oversell-capstone", "review"),
        ("row-lock", "new"),
    ]
