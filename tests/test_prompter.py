from utils.prompter import prompt_for_config

HEADING = {
    "before": [
        {
            "title": "Section",
            "prompts": [
                {"key": "name", "prompt": "Name", "required": True},
                {"key": "note", "prompt": "Note", "default": "hello"},
                {"key": "tags", "prompt": "Tags", "is_list": True, "default": "a,b"},
            ],
        }
    ]
}


def test_overrides_satisfy_all_fields_without_prompting():
    config = prompt_for_config(HEADING, overrides={"name": "web", "note": "custom"})

    assert config == {"name": "web", "note": "custom", "tags": ["a", "b"]}


def test_no_overrides_prompts_interactively(monkeypatch):
    monkeypatch.setattr(
        "utils.prompter.Prompt.ask", lambda *a, **kw: kw.get("default") or "answer"
    )

    config = prompt_for_config(HEADING)

    assert config == {"name": "answer", "note": "hello", "tags": ["a", "b"]}


def test_missing_required_field_still_prompts(monkeypatch):
    calls = []

    def fake_ask(prompt, **kwargs):
        calls.append(prompt)
        return "prompted-name" if prompt == "Name" else kwargs.get("default")

    monkeypatch.setattr("utils.prompter.Prompt.ask", fake_ask)

    config = prompt_for_config(HEADING, overrides={"note": "custom"})

    assert calls == ["Name"]
    assert config == {"name": "prompted-name", "note": "custom", "tags": ["a", "b"]}
