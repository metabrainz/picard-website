import json
import os
import shutil
import tempfile
import zipfile

import pytest


TEST_PLUGINS_DATA = {
    "plugins": {
        "addrelease": {
            "name": "Add Cluster As Release",
            "api_versions": ["0.15.0", "0.15.1", "0.16.0", "1.0.0"],
            "author": "Test Author",
            "description": "Test plugin",
            "version": "0.1",
            "files": {"__init__.py": "d41d8cd98f00b204e9800998ecf8427e"},
        }
    }
}


@pytest.fixture(autouse=True, scope="session")
def plugins_build_dir():
    """Create a temporary plugins directory with test data for all tests."""
    tmp_dir = tempfile.mkdtemp(prefix="picard_test_plugins_")
    for version in ("1.0", "2.0"):
        version_dir = os.path.join(tmp_dir, version)
        os.makedirs(version_dir, exist_ok=True)
        with open(os.path.join(version_dir, "plugins.json"), "w") as f:
            json.dump(TEST_PLUGINS_DATA, f)
        # Create a zip file for the download test
        zip_path = os.path.join(version_dir, "addrelease.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("__init__.py", "# test plugin")

    os.environ["PICARD_WEBSITE_TEST_PLUGINS_DIR"] = tmp_dir
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)
