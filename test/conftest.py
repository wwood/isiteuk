import pytest


def pytest_addoption(parser):
    parser.addoption("--run-expensive", action="store_true", help="run expensive tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "expensive: mark test as requiring --run-expensive")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-expensive"):
        return
    skip_expensive = pytest.mark.skip(reason="need --run-expensive option to run")
    for item in items:
        if "expensive" in item.keywords:
            item.add_marker(skip_expensive)
