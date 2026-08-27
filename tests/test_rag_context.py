import json

from create_app.rag_context import write_project_context


def test_local_rag_context_excludes_secrets_and_runtime_output(tmp_path):
    (tmp_path / "app.py").write_text("print('ok')\n")
    (tmp_path / ".env").write_text("TOKEN=secret\n")
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "ignored.py").write_text("secret")
    (tmp_path / "data.sqlite3").write_text("not text for indexing")

    write_project_context(tmp_path, {"project name": "sample", "fw_name": "fastapi"})
    context = json.loads((tmp_path / ".init-app" / "rag-context.json").read_text())

    assert context["indexing"]["mode"] == "local_only"
    assert "app.py" in context["inventory"]["files"]
    assert ".env" not in context["inventory"]["files"]
    assert "venv/ignored.py" not in context["inventory"]["files"]
    assert "data.sqlite3" not in context["inventory"]["files"]
    assert (tmp_path / "docs" / "LOCAL_RAG.md").exists()
