from create_app.engine.ui.user_interface import InitUI


def test_custom_folder_input_accepts_nested_and_bracketed_paths():
    folders, invalid = InitUI._parse_custom_folders("[src/api, tests/unit, src/api]")
    assert folders == ["src/api", "tests/unit"]
    assert invalid == []


def test_custom_folder_input_rejects_paths_outside_the_project():
    folders, invalid = InitUI._parse_custom_folders("src, ../outside, /absolute, C:\\temp")
    assert folders == ["src"]
    assert invalid == ["../outside", "/absolute", "C:\\temp"]
