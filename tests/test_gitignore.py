import pytest

from create_app.gitignore import normalize_patterns, render_gitignore


def test_framework_preset_and_custom_bracket_list():
    content = render_gitignore("framework", "django", ["[uploads/, *.secret, .env.local]"])
    assert "db.sqlite3" in content
    assert "uploads/" in content
    assert "*.secret" in content
    assert ".env.local" in content


def test_patterns_accept_separate_and_bracketed_values_without_duplicates():
    assert normalize_patterns([".env", "[logs/, .env, *.local]"]) == [".env", "logs/", "*.local"]
    assert normalize_patterns("[cache/, *.tmp]") == ["cache/", "*.tmp"]


def test_multiline_pattern_is_rejected():
    with pytest.raises(ValueError):
        normalize_patterns(["safe\nunsafe"])
