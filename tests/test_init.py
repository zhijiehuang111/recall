import tomllib


def test_init_creates_recall_dir_with_default_config(vault):
    vault.root.mkdir()

    result = vault.init_script()

    assert result.code == 0, result.stderr
    assert result.json() == {"recall": str(vault.recall), "created": True}
    assert (vault.recall / "cards").is_dir()
    assert (vault.recall / "topics").is_dir()
    assert (vault.recall / ".rubrics").is_dir()
    config = tomllib.loads((vault.recall / "config.toml").read_text())
    assert config["daily_minutes"] == 30
    assert config["target_roles"] == []
    assert config["roadmap_sources"] == [
        "https://roadmap.sh/backend",
        "https://roadmap.sh/full-stack",
        "https://roadmap.sh/ai-engineer",
    ]
    # 新建的 Vault 立刻能讓 due 讀
    assert vault.due("--today", "2026-11-03").json()["cards"] == []


def test_init_on_existing_recall_dir_keeps_everything_as_is(ready_vault):
    ready_vault.add_card("sql-having")
    config = ready_vault.recall / "config.toml"
    config.write_text("daily_minutes = 45\n")

    result = ready_vault.init_script()

    assert result.code == 0, result.stderr
    assert result.json()["created"] is False
    assert config.read_text() == "daily_minutes = 45\n"
    assert [
        c["card"] for c in ready_vault.due("--today", "2026-11-03").json()["cards"]
    ] == ["sql-having"]


def test_init_refuses_a_vault_path_that_does_not_exist(vault, tmp_path):
    result = vault.init_script("--vault", str(vault.root), cwd=tmp_path)

    assert result.code != 0
    assert str(vault.root) in result.stderr
    assert not vault.root.exists()
