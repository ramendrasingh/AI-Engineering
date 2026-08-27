import pytest

from app.tool.search_files import SearchFilesTool


@pytest.fixture
def tool(tmp_path):
    return SearchFilesTool(
        workspace_root=str(tmp_path),
        max_result=10,
    )


def test_valid_arguments(tool):
    tool.validate_arguments({"query": "architecture"})


def test_missing_query(tool):
    with pytest.raises(ValueError, match="Missing required argument"):
        tool.validate_arguments({})


def test_empty_query(tool):
    with pytest.raises(ValueError, match="cannot be empty"):
        tool.validate_arguments({"query": "   "})


def test_non_string_query(tool):
    with pytest.raises(ValueError, match="must be a string"):
        tool.validate_arguments({"query": 123})
