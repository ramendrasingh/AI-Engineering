import pytest
from pydantic import ValidationError

from app.models.schemas import (
    ListDirectoryArguments,
    ReadFileArguments,
    SearchFilesArguments,
)


def test_search_files_valid_arguments():
    arguments = SearchFilesArguments(query="architecture")

    assert arguments.query == "architecture"


def test_search_files_empty_query():
    with pytest.raises(ValidationError):
        SearchFilesArguments(query="")


def test_read_file_valid_arguments():
    arguments = ReadFileArguments(path="knowledge/api.md")

    assert arguments.path == "knowledge/api.md"


def test_read_file_empty_path():
    with pytest.raises(ValidationError):
        ReadFileArguments(path="")


def test_list_directory_with_path():
    arguments = ListDirectoryArguments(path="knowledge")

    assert arguments.path == "knowledge"


def test_list_directory_default_path():
    arguments = ListDirectoryArguments()

    assert arguments.path == "."


def test_search_files_requires_query():
    with pytest.raises(ValidationError):
        SearchFilesArguments()


def test_read_file_requires_path():
    with pytest.raises(ValidationError):
        ReadFileArguments()


def test_search_files_json_schema():
    schema = SearchFilesArguments.model_json_schema()

    assert schema["properties"]["query"]["type"] == "string"
    assert "query" in schema["required"]


def test_read_file_json_schema():
    schema = ReadFileArguments.model_json_schema()

    assert schema["properties"]["path"]["type"] == "string"
    assert "path" in schema["required"]


def test_list_directory_json_schema():
    schema = ListDirectoryArguments.model_json_schema()

    assert schema["properties"]["path"]["type"] == "string"
