from utils.overrides import apply_override, build_overrides, split_csv


def test_split_csv_strips_and_drops_blanks():
    assert split_csv("a, b ,, c") == ["a", "b", "c"]
    assert split_csv(["already", "a", "list"]) == ["already", "a", "list"]


def test_apply_override_rejects_missing_required():
    accepted, _ = apply_override({"key": "k", "required": True}, "")
    assert not accepted


def test_apply_override_rejects_bad_regex():
    accepted, _ = apply_override({"key": "k", "regex": r"^\d+$"}, "abc")
    assert not accepted


def test_apply_override_rejects_bad_choice():
    accepted, _ = apply_override({"key": "k", "choices": ["a", "b"]}, "c")
    assert not accepted


def test_apply_override_splits_list_values():
    accepted, value = apply_override({"key": "k", "is_list": True}, "a,b,c")
    assert accepted
    assert value == ["a", "b", "c"]


def test_build_overrides_values_file(tmp_path):
    values_file = tmp_path / "values.yaml"
    values_file.write_text("backup_name: web\nsource_directory: /srv/www\n")

    overrides = build_overrides(str(values_file), [])

    assert overrides == {"backup_name": "web", "source_directory": "/srv/www"}


def test_build_overrides_set_flags_take_precedence(tmp_path):
    values_file = tmp_path / "values.yaml"
    values_file.write_text("backup_name: from-file\n")

    overrides = build_overrides(str(values_file), ["backup_name=from-set"])

    assert overrides["backup_name"] == "from-set"


def test_build_overrides_ignores_malformed_set(capsys):
    overrides = build_overrides(None, ["no-equals-sign"])

    assert overrides == {}
    assert "malformed" in capsys.readouterr().out.lower()


def test_build_overrides_missing_values_file(capsys):
    overrides = build_overrides("/no/such/file.yaml", [])

    assert overrides == {}
    assert "not found" in capsys.readouterr().out.lower()
