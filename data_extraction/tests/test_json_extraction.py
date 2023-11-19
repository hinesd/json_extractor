import pytest
import os
from json_extractor.data_extraction.json_extractor import json_extractor


@pytest.mark.parametrize("filename", os.listdir('tests/test_files'))
def test_json_extraction(filename):
    file_path = os.path.join("tests/test_files", filename)
    with open(file_path, "r") as file:
        file_content = file.read()
        result = json_extractor(file_content)
        assert len(result) > 0, f"Failed for file: {filename}"
