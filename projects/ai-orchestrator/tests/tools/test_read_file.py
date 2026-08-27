import pytest

from app.tool.read_file import ReadFileTool


@pytest.fixture
def tool(tmp_path):
    return ReadFileTool(workspace_root=str(tmp_path))


def test_valid_arguments(tool):
    tool.validate_arguments({"path": "knowledge/api.md"})


def test_missing_path(tool):
    with pytest.raises(ValueError, match="Missing required argument"):
        tool.validate_arguments({})


def test_empty_path(tool):
    with pytest.raises(ValueError, match="cannot be empty"):
        tool.validate_arguments({"path": "   "})


def test_non_string_path(tool):
    with pytest.raises(ValueError, match="must be a string"):
        tool.validate_arguments({"path": 123})
